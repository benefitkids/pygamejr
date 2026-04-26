"""End-to-end tests for the ``codomir`` quest layer.

Importing ``codomir`` has heavy module-level side effects: it loads the
default tilemap, builds a scene, instantiates the ``player`` singleton and
renders a frame. Player movement also blocks for ~60 frames per tile and the
win/game-over animations are multi-second by design. To keep tests fast and
hermetic, every scenario runs in a fresh Python subprocess that monkey-patches
the slow animations to no-ops.
"""
import os
import subprocess
import sys
import textwrap

import pytest


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
