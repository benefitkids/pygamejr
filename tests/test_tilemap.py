"""Tests for ``pygamejr.tilemap.TileMap``."""
import pygame
import pygamejr
from codomir.maps import linear, loop


def test_tilemap_loads_walls_layer():
    tilemap = pygamejr.TileMap(linear.map1)
    walls = tilemap.get_layer_sprites("walls")
    assert isinstance(walls, list)
    assert walls, "walls layer should not be empty for linear.map1"
    for sprite in walls:
        assert isinstance(sprite, pygamejr.ImageSprite)
        assert sprite.image is not None


def test_tilemap_walls_positioned_on_tile_grid():
    tilemap = pygamejr.TileMap(linear.map1)
    tw = tilemap.tmxdata.tilewidth
    th = tilemap.tmxdata.tileheight
    for sprite in tilemap.get_layer_sprites("walls"):
        assert sprite.rect.x % tw == 0
        assert sprite.rect.y % th == 0


def test_tilemap_get_sprite_by_tileset_position_returns_image_sprite():
    tilemap = pygamejr.TileMap(linear.map1)
    # Walk the first row of the tileset to find a tile that is not entirely
    # transparent. The Sokoban sheet has empty leading slots which would be
    # cropped to a 0×N surface by the default ``crop_alpha`` behaviour.
    found = None
    for col in range(8):
        sprite = tilemap.get_sprite_by_tileset_position(0, col)
        if sprite.image.get_width() > 0 and sprite.image.get_height() > 0:
            found = sprite
            break
    assert found is not None, "no non-empty tile found in first tileset row"
    assert isinstance(found, pygamejr.ImageSprite)


def test_tilemap_loop_map_loads_layers():
    tilemap = pygamejr.TileMap(loop.map1)
    walls = tilemap.get_layer_sprites("walls")
    assert walls
