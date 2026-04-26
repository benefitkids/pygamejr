"""Tests for ``pygamejr.scene.Scene``."""
import pygame
import pygamejr
from pygamejr.scene import DEFAULT_LAYER, Scene


def _isolated_scene():
    """Return a Scene that won't be polluted by the global module state."""
    scene = Scene()
    return scene


def test_default_layer_present_after_init():
    scene = _isolated_scene()
    layer = scene.get_sprite_list(DEFAULT_LAYER)
    assert layer is not None
    assert len(layer) == 0


def test_get_sprite_list_returns_none_for_unknown_layer():
    scene = _isolated_scene()
    assert scene.get_sprite_list("not-a-layer") is None


def test_add_and_remove_sprite_uses_default_layer():
    previous = pygamejr.get_current_scene()
    try:
        scene = Scene()
        pygamejr.set_scene(scene)
        sprite = pygamejr.RectSprite(width=10, height=10)
        layer = scene.get_sprite_list(DEFAULT_LAYER)
        assert sprite in layer

        scene.remove(sprite)
        assert sprite not in layer
    finally:
        pygamejr.set_scene(previous)


def test_add_sprite_list_registers_named_group():
    scene = _isolated_scene()
    group = pygame.sprite.LayeredUpdates()
    scene.add_sprite_list("walls", group)
    assert scene.get_sprite_list("walls") is group


def test_pending_transition_starts_unset():
    scene = _isolated_scene()
    assert scene.pending_transition is None


def test_update_propagates_dt_to_groups(monkeypatch):
    scene = _isolated_scene()
    seen = []

    class FakeGroup:
        def update(self, dt):
            seen.append(dt)

        def __iter__(self):
            return iter(())

    scene._name_mapping[DEFAULT_LAYER] = FakeGroup()
    scene.add_sprite_list("extra", FakeGroup())
    scene.update(0.25)
    assert seen == [0.25, 0.25]


def test_from_tilemap_creates_named_layers_and_clears_default():
    from codomir.maps.linear import map1

    previous = pygamejr.get_current_scene()
    try:
        tilemap = pygamejr.TileMap(map1)
        scene = Scene.from_tilemap(tilemap)
        assert scene.get_sprite_list("walls") is not None
        assert len(scene.get_sprite_list(DEFAULT_LAYER)) == 0
        assert pygamejr.get_current_scene() is previous
    finally:
        pygamejr.set_scene(previous)
