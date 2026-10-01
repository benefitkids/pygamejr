"""End-to-end tests for the ``codomir`` quest layer.

Importing ``codomir`` has heavy module-level side effects: it loads the
default tilemap, builds a scene, instantiates the ``player`` singleton and
renders a frame. Player movement also blocks for ~60 frames per tile and the
win/game-over animations are multi-second by design. To keep tests fast and
hermetic, every scenario runs in a fresh Python subprocess that monkey-patches
the slow animations to no-ops.
"""
import os
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest


@pytest.mark.parametrize("number", range(7, 21))
def test_new_linear_map_solution_reaches_goal(number):
    """Catch missing resources, blocked routes and incorrect demo commands."""
    demo = Path(__file__).resolve().parents[1] / "demo" / "codomir" / f"map{number}.py"
    result = _run(
        f"""
        import ast
        import runpy
        from pathlib import Path
        import pygamejr

        set_map(getattr(maps.linear, "map{number}"))
        # Keep all movement updates, but skip frame delays and the demo window loop.
        pygamejr.every_frame = lambda count: iter([0] * count)
        pygamejr.next_frame = lambda: None
        codomir.wait_quit = lambda: None

        source = Path({str(demo)!r}).read_text(encoding="utf-8")
        tree = ast.parse(source)
        assert all(isinstance(node, (ast.ImportFrom, ast.Expr)) for node in tree.body), \
            "The learner's solution must contain only sequential commands"
        runpy.run_path({str(demo)!r})
        assert player.is_finished and player.is_win
        assert not player.is_game_over
        print("ok")
        """
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


@pytest.mark.parametrize("number", range(7, 21))
def test_new_loop_map_solution_reaches_goal_without_nested_loops(number):
    demo = Path(__file__).resolve().parents[1] / "demo" / "codomir" / "loop" / f"map{number}.py"
    result = _run(
        f"""
        import ast
        import runpy
        from pathlib import Path
        import pygamejr

        set_map(getattr(maps.loop, "map{number}"))
        pygamejr.every_frame = lambda count: iter([0] * count)
        pygamejr.next_frame = lambda: None
        codomir.wait_quit = lambda: None

        tree = ast.parse(Path({str(demo)!r}).read_text(encoding="utf-8"))
        loops = [node for node in tree.body if isinstance(node, ast.For)]
        assert loops, "The solution must practice for loops"
        assert all(isinstance(node, (ast.ImportFrom, ast.Expr, ast.For)) for node in tree.body)
        for loop in loops:
            assert all(isinstance(node, ast.Expr) for node in loop.body), "No nested loops or conditions"
            assert not loop.orelse
            assert isinstance(loop.iter, ast.Call)
            assert isinstance(loop.iter.func, ast.Name) and loop.iter.func.id == "range"
        runpy.run_path({str(demo)!r})
        assert player.is_finished and player.is_win
        assert not player.is_game_over
        print("ok")
        """
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


@pytest.mark.parametrize("number", range(1, 23))
def test_nested_map_solution_and_geometry(number):
    """Every example fits the window and follows an unambiguous nested route."""
    demo = Path(__file__).resolve().parents[1] / "demo" / "codomir" / "nested_loop" / f"map{number}.py"
    result = _run(
        f"""
        import ast
        import runpy
        from pathlib import Path
        import pygamejr
        import codomir.quest as quest

        source = Path({str(demo)!r}).read_text(encoding="utf-8")
        tree = ast.parse(source)

        def check_body(body, depth=0):
            deepest = depth
            for node in body:
                assert isinstance(node, (ast.ImportFrom, ast.Expr, ast.For))
                if isinstance(node, ast.For):
                    assert not node.orelse
                    assert isinstance(node.target, ast.Name)
                    assert node.target.id == ('i', 'j', 'k')[depth]
                    assert isinstance(node.iter, ast.Call)
                    assert isinstance(node.iter.func, ast.Name)
                    assert node.iter.func.id == 'range'
                    deepest = max(deepest, check_body(node.body, depth + 1))
                elif isinstance(node, ast.Expr):
                    assert isinstance(node.value, ast.Call)
                    func = node.value.func
                    if isinstance(func, ast.Attribute):
                        assert isinstance(func.value, ast.Name) and func.value.id == 'player'
                        assert func.attr in ('move_forward', 'turn_left', 'turn_right')
                        assert not node.value.args and not node.value.keywords
                    else:
                        assert isinstance(func, ast.Name)
                        assert func.id in ('set_map', 'wait_quit')
            return deepest

        assert check_body(tree.body) == {3 if number >= 21 else 2}
        if {number} >= 21:
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    assert all(isinstance(arg, ast.Constant) for arg in node.iter.args)
                    assert len(range(*(arg.value for arg in node.iter.args))) >= 2

        pygamejr.every_frame = lambda count: iter([0] * count)
        pygamejr.next_frame = lambda: None
        codomir.wait_quit = lambda: None
        set_map(getattr(maps.nested_loops, 'map{number}'))
        tm = quest.tilemap.tmxdata
        assert (tm.width, tm.height, tm.tilewidth, tm.tileheight) == (8, 8, 64, 64)
        assert pygamejr.screen.get_size() == (512, 512)
        walls = tm.layernames['walls'].data
        for kind in ('Spawn', 'Win'):
            positions = [(x, y) for x, y, gid in tm.layernames['objects']
                         if gid and tm.tile_properties[gid].get('type') == kind]
            assert len(positions) == 1, (kind, positions)
            x, y = positions[0]
            assert not walls[y][x]

        path = [(player._tile_x, player._tile_y)]
        move = player._move_to
        def checked_move(x, y):
            assert not player.is_finished, 'Extra move after reaching the finish'
            assert 0 <= x < tm.width and 0 <= y < tm.height, (x, y)
            assert not walls[y][x], (x, y)
            move(x, y)
            path.append((x, y))
        player._move_to = checked_move

        runpy.run_path({str(demo)!r})
        assert player.is_win and not player.is_game_over
        assert path[-1] == quest.win_position
        assert len(path) == len(set(path)), 'Route crosses itself'
        for a, (x, y) in enumerate(path):
            for b in range(a + 2, len(path)):
                bx, by = path[b]
                assert abs(x - bx) + abs(y - by) != 1, 'Route has a shortcut'
        free = {{(x, y) for y, row in enumerate(walls) for x, gid in enumerate(row) if not gid}}
        assert free == set(path), 'Unexplained open cells outside the route'
        print('ok')
        """
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout


def _run(snippet: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a Python snippet in a fresh subprocess with SDL dummy drivers.

    The snippet is wrapped with the standard codomir stub so each test only
    needs to provide the body of the scenario.
    """
    program = textwrap.dedent(
        """
        import os, sys
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        import codomir
        from codomir import player, set_map, maps

        # Stub the slow end-of-quest animations.
        player._animate_win = lambda: None
        player._animate_game_over = lambda dx, dy: None
        """
    ) + textwrap.dedent(snippet)
    env = os.environ.copy()
    env["SDL_VIDEODRIVER"] = "dummy"
    env["SDL_AUDIODRIVER"] = "dummy"
    return subprocess.run(
        [sys.executable, "-c", program],
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_codomir_imports_and_player_is_alive():
    result = _run(
        """
        assert player is not None
        assert player.is_finished is False
        assert player.is_win is False
        assert player.is_game_over is False
        print("ok")
        """
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_codomir_default_map_win_path():
    """Two forward steps on the default map should reach the win tile."""
    result = _run(
        """
        player.move_forward()
        player.move_forward()
        assert player.is_finished, "expected finished"
        assert player.is_win, "expected win"
        assert not player.is_game_over
        print("ok")
        """
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_codomir_default_map_game_over_path():
    """Turning into a wall should trigger game-over."""
    result = _run(
        """
        player.turn_left()
        player.move_forward()
        assert player.is_finished
        assert player.is_game_over
        assert not player.is_win
        print("ok")
        """
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_codomir_turn_cycle_returns_to_start():
    """Four right turns should land back on the original direction."""
    result = _run(
        """
        from codomir.quest import Direction
        original = player._direction
        for _ in range(4):
            player.turn_right()
        assert player._direction == original
        for _ in range(4):
            player.turn_left()
        assert player._direction == original
        print("ok")
        """
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_codomir_set_map_resets_player_state():
    result = _run(
        """
        # First win the default map.
        player.move_forward()
        player.move_forward()
        assert player.is_finished and player.is_win

        set_map(maps.linear.map3)
        assert not player.is_finished
        assert not player.is_win
        assert not player.is_game_over
        print("ok")
        """
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_codomir_on_complete_callback_fires_with_true_on_win():
    result = _run(
        """
        results = []
        player.on_complete = lambda success: results.append(success)
        player.move_forward()
        player.move_forward()
        assert results == [True], results
        print("ok")
        """
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_codomir_on_complete_callback_fires_with_false_on_game_over():
    result = _run(
        """
        results = []
        player.on_complete = lambda success: results.append(success)
        player.turn_left()
        player.move_forward()
        assert results == [False], results
        print("ok")
        """
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_codomir_window_size_is_overridden_to_512():
    result = _run(
        """
        import pygamejr
        assert pygamejr.screen.get_size() == (512, 512), pygamejr.screen.get_size()
        print("ok")
        """
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_codomir_player_reset_clears_finished_flags():
    result = _run(
        """
        player.move_forward()
        player.move_forward()
        assert player.is_finished and player.is_win
        player.reset()
        assert not player.is_finished
        assert not player.is_win
        assert not player.is_game_over
        print("ok")
        """
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout
