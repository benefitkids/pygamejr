"""Tests for the sprite hierarchy under ``pygamejr.sprite``."""
import math
import time

import pygame
import pytest

import pygamejr
from pygamejr.sprite.base import BaseSprite
from pygamejr.sprite.subtitles import SubtitlesSprite


@pytest.fixture
def isolated_scene():
    """Provide a fresh current scene per test so sprites land predictably."""
    previous = pygamejr.get_current_scene()
    scene = pygamejr.Scene()
    pygamejr.set_scene(scene)
    try:
        yield scene
    finally:
        pygamejr.set_scene(previous)


def test_circle_sprite_has_expected_dimensions(isolated_scene):
    circle = pygamejr.CircleSprite(color="blue", radius=20)
    assert circle.image.get_size() == (40, 40)
    assert circle.rect.width == 40 and circle.rect.height == 40
    assert circle in isolated_scene.get_sprite_list("default")


def test_rect_sprite_has_expected_dimensions(isolated_scene):
    rect = pygamejr.RectSprite(width=30, height=15)
    assert rect.image.get_size() == (30, 15)
    assert rect.rect.width == 30 and rect.rect.height == 15


def test_text_sprite_renders_size_grows_with_text(isolated_scene):
    short = pygamejr.TextSprite("a", size=20)
    short_width = short.rect.width
    short.text = "aaaaaaaaaaaa"
    assert short.rect.width > short_width


def test_text_sprite_setter_no_op_when_unchanged(isolated_scene):
    sprite = pygamejr.TextSprite("hello", size=20)
    image_before = sprite.image
    sprite.text = "hello"
    assert sprite.image is image_before


def test_image_sprite_from_surface_does_not_load_file(isolated_scene):
    surface = pygame.Surface((24, 18), pygame.SRCALPHA)
    surface.fill((10, 20, 30, 255))
    sprite = pygamejr.ImageSprite(image=surface, crop_alpha=False)
    assert sprite.image.get_size() == (24, 18)
    assert sprite.mask is not None


def test_image_sprite_requires_filename_or_image(isolated_scene):
    with pytest.raises(ValueError):
        pygamejr.ImageSprite()


def test_image_sprite_set_image_preserves_center(isolated_scene):
    first = pygame.Surface((20, 20), pygame.SRCALPHA)
    first.fill((255, 0, 0, 255))
    second = pygame.Surface((40, 40), pygame.SRCALPHA)
    second.fill((0, 255, 0, 255))

    sprite = pygamejr.ImageSprite(image=first, crop_alpha=False)
    sprite.rect.center = (123, 456)
    sprite.set_image(image=second, crop_alpha=False)
    assert sprite.rect.center == (123, 456)
    assert sprite.image.get_size() == (40, 40)


def test_image_sprite_rotate_updates_angle_and_image(isolated_scene):
    surface = pygame.Surface((20, 10), pygame.SRCALPHA)
    surface.fill((255, 255, 255, 255))
    sprite = pygamejr.ImageSprite(image=surface, crop_alpha=False)
    image_before = sprite.image
    sprite.rotate(90)
    assert sprite._angle == 90
    assert sprite.image is not image_before
    sprite.turn_left(45)
    assert sprite._angle == 45
    sprite.turn_right(45)
    assert sprite._angle == 90


def test_image_sprite_crop_alpha_trims_transparent_border(isolated_scene):
    surface = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.rect(surface, (200, 50, 50, 255), pygame.Rect(10, 12, 6, 8))
    sprite = pygamejr.ImageSprite(image=surface, crop_alpha=True)
    assert sprite.image.get_size() == (6, 8)


def test_base_sprite_visibility_toggle(isolated_scene):
    sprite = pygamejr.RectSprite(width=10, height=10)
    assert sprite.is_visible is True
    sprite.is_visible = False
    assert sprite.is_visible is False


def test_base_sprite_move_forward_with_angle(isolated_scene):
    sprite = pygamejr.RectSprite(width=10, height=10)
    sprite.rect.x = 0
    sprite.rect.y = 0
    sprite._angle = 90
    sprite.move_forward(distance=10)
    assert sprite.rect.x == pytest.approx(10, abs=1e-6)
    assert sprite.rect.y == pytest.approx(0, abs=1e-6)


def test_base_sprite_rotate_wraps_at_360(isolated_scene):
    sprite = pygamejr.RectSprite(width=10, height=10)
    sprite._angle = 350
    sprite.rotate(20)
    assert sprite._angle == 10


def test_base_sprite_added_to_global_when_no_current_scene():
    previous = pygamejr.get_current_scene()
    pygamejr.set_scene(None)
    try:
        sprite = pygamejr.RectSprite(width=5, height=5)
        global_layer = pygamejr.get_global_scene().get_sprite_list("default")
        assert sprite in global_layer
    finally:
        pygamejr.set_scene(previous)


def test_subtitles_sprite_visibility_drives_render(isolated_scene):
    subs = SubtitlesSprite(text_list=["one", "two"], size=18)
    assert subs.text == "one"
    assert subs.is_visible is False

    subs.visible = 1
    subs.update()
    assert subs.is_visible is True


def test_subtitles_sprite_advances_after_timeout(isolated_scene):
    subs = SubtitlesSprite(text_list=["one", "two"], size=18)
    subs.visible = 1
    subs._last_update = time.time() - 5  # force timeout
    subs.update()
    assert subs.text == "two"


def test_subtitles_sprite_resets_after_last_line(isolated_scene):
    subs = SubtitlesSprite(text_list=["one", "two"], size=18)
    subs.visible = 1
    subs._text_index = 1
    subs._last_update = time.time() - 5
    subs.update()
    assert subs._text_index == 0
    assert subs.is_visible is False
