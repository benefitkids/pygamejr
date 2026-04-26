"""Tests for the ``pygamejr.base`` module: screen, scenes, frame loop."""
import os
import subprocess
import sys
import textwrap

import pygame
import pygamejr
from pygamejr import base


def test_screen_uses_module_configured_size():
    """``pygamejr.screen`` must match the size cached during module import."""
    assert pygamejr.screen is base.screen
    assert pygamejr.screen.get_size() == (base.window_width, base.window_height)


def test_screen_size_in_subprocess_with_env(tmp_path):
    """Module-level env vars should drive the screen size on import."""
    script = tmp_path / "size_check.py"
    script.write_text(
        textwrap.dedent(
            """
            import os
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            os.environ["SDL_AUDIODRIVER"] = "dummy"
            os.environ["PYGAMEJR_WINDOW_WIDTH"] = "320"
            os.environ["PYGAMEJR_WINDOW_HEIGHT"] = "240"
            import pygamejr
            assert pygamejr.screen.get_size() == (320, 240), pygamejr.screen.get_size()
            print("ok")
            """
        )
    )
    env = os.environ.copy()
    result = subprocess.run(
        [sys.executable, str(script)],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_get_global_scene_is_singleton():
    g1 = pygamejr.get_global_scene()
    g2 = pygamejr.get_global_scene()
    assert g1 is g2


def test_set_scene_and_get_current_scene_round_trip():
    previous = pygamejr.get_current_scene()
    try:
        scene = pygamejr.Scene()
        pygamejr.set_scene(scene)
        assert pygamejr.get_current_scene() is scene
        pygamejr.set_scene(None)
        assert pygamejr.get_current_scene() is None
    finally:
        pygamejr.set_scene(previous)


def test_set_scene_calls_init_scene_hook():
    previous = pygamejr.get_current_scene()
    calls = []

    class TrackingScene(pygamejr.Scene):
        def init_scene(self):
            calls.append("init")

    try:
        scene = TrackingScene()
        pygamejr.set_scene(scene)
        assert calls == ["init"]
    finally:
        pygamejr.set_scene(previous)


def test_every_frame_yields_requested_number_of_frames():
    """``every_frame(N)`` yields ``N + 1`` dt values (the loop checks
    ``frame >= frame_count`` *after* the initial value of ``frame == -1``,
    so it produces one bonus frame). Pinning the actual behaviour here
    protects future refactors from silently changing it.
    """
    dts = list(pygamejr.every_frame(3))
    assert len(dts) == 4
    assert all(isinstance(dt, float) for dt in dts)
    assert all(dt >= 0 for dt in dts)


def test_every_frame_with_count_one_still_yields_two_frames():
    yielded = 0
    for _ in pygamejr.every_frame(1):
        yielded += 1
    assert yielded == 2


def test_next_frame_returns_true_when_not_quit():
    assert pygamejr.next_frame() is True


def test_next_frame_renders_current_scene(monkeypatch):
    previous = pygamejr.get_current_scene()
    calls = {"update": 0, "draw": 0}

    class CountingScene(pygamejr.Scene):
        def update(self, dt=0):
            calls["update"] += 1

        def draw(self, draw_rect=False):
            calls["draw"] += 1

    try:
        scene = CountingScene()
        pygamejr.set_scene(scene)
        pygamejr.next_frame()
        assert calls["update"] >= 1
        assert calls["draw"] >= 1
    finally:
        pygamejr.set_scene(previous)


def test_is_quit_returns_false_when_no_quit_event():
    pygame.event.clear(pygame.QUIT)
    assert pygamejr.is_quit() is False


def test_is_quit_becomes_true_after_quit_event_in_subprocess(tmp_path):
    """``is_quit`` is sticky module-level; verify in a fresh subprocess."""
    script = tmp_path / "quit_check.py"
    script.write_text(
        textwrap.dedent(
            """
            import os
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            os.environ["SDL_AUDIODRIVER"] = "dummy"
            import pygame
            import pygamejr

            assert pygamejr.is_quit() is False
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            assert pygamejr.is_quit() is True
            assert pygamejr.is_quit() is True
            print("ok")
            """
        )
    )
    env = os.environ.copy()
    env["SDL_VIDEODRIVER"] = "dummy"
    env["SDL_AUDIODRIVER"] = "dummy"
    result = subprocess.run(
        [sys.executable, str(script)],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout
