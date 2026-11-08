from enum import Enum
import os
import json
import pygame
from pygame.sprite import Group
from pytmx import TiledObjectGroup, TiledTileLayer

# https://stackoverflow.com/questions/4135928/pygame-display-position
pygame.init()

display_info = pygame.display.Info()
screen_width = display_info.current_w

window_width = 8*64
window_height = 8*64
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (screen_width - window_width, 50)
os.environ['PYGAMEJR_WINDOW_WIDTH'] = f"{window_width}"
os.environ['PYGAMEJR_WINDOW_HEIGHT'] = f"{window_height}"

import pygamejr
from pygamejr.scene import DEFAULT_LAYER
from pygamejr.sprite.base import BaseSprite
from .maps.linear import map1

from pytmx.util_pygame import load_pygame, pygame_image_loader

tilemap = pygamejr.TileMap(map1)

CHARACTER_TILES = {
    'right':  json.loads(tilemap.tmxdata.properties['character_right'])  if 'character_right'  in tilemap.tmxdata.properties else None,
    'bottom': json.loads(tilemap.tmxdata.properties['character_bottom']) if 'character_bottom' in tilemap.tmxdata.properties else None,
    'left':   json.loads(tilemap.tmxdata.properties['character_left'])   if 'character_left'   in tilemap.tmxdata.properties else None,
    'top':    json.loads(tilemap.tmxdata.properties['character_top'])    if 'character_top'    in tilemap.tmxdata.properties else None,
}

# Workaround for a pytmx bug: load_all_tiles option does not work.
def load_image(tile_x, tile_y):
    ts = tilemap.tmxdata.tilesets[0]
    colorkey = getattr(ts, "trans", None)
    path = os.path.join(os.path.dirname(tilemap.tmxdata.filename), ts.source)
    loader = pygame_image_loader(path, colorkey, tileset=ts)
    rect = (tile_x * ts.tilewidth, tile_y * ts.tileheight, ts.tilewidth, ts.tileheight)
    return loader(rect, None)


TILE_SIZE = 64


class Direction(Enum):
    TOP = 1
    RIGHT = 2
    BOTTOM = 3
    LEFT = 4


directions = (Direction.TOP, Direction.RIGHT, Direction.BOTTOM, Direction.LEFT)


def _get_spawn_position():
    return _get_position_by_type('Spawn')


def _get_win_position():
    return _get_position_by_type('Win')


def _get_position_by_type(tile_type, source=None):
    data = (source or tilemap).tmxdata
    for tile in data.layernames['objects']:
        tile_id = tile[2]
        if tile_id and data.tile_properties.get(tile_id, {}).get('type') == tile_type:
            return tile[0], tile[1]
    return 0, 0


def _get_initial_boxes(tilemap):
    """Validate Box tiles before creating sprites or replacing the active map."""
    data = tilemap.tmxdata
    if sum(layer.name == 'boxes' for layer in data.layers) > 1:
        raise ValueError("The map must have at most one boxes layer")
    spawn_positions = {
        (x, y) for x, y, gid in data.layernames['objects']
        if data.tile_properties.get(gid, {}).get('type') == 'Spawn'
    }
    boxes = []
    for layer in data.layers:
        if layer.name == 'boxes':
            if not isinstance(layer, TiledTileLayer):
                raise ValueError("The boxes layer must be a tile layer")
            if (layer.width, layer.height) != (data.width, data.height):
                raise ValueError("The boxes layer dimensions must match the map")
            if any(getattr(layer, name, 0) for name in ('x', 'y', 'offsetx', 'offsety')):
                raise ValueError("The boxes layer must not have an offset")
        if isinstance(layer, TiledObjectGroup):
            for obj in layer:
                properties = data.tile_properties.get(getattr(obj, 'gid', 0), {})
                if obj.type == 'Box' or properties.get('type') == 'Box':
                    raise ValueError("Box objects must be tiles in the boxes layer")
        if not isinstance(layer, TiledTileLayer):
            continue
        for x, y, gid in layer:
            if not gid:
                continue
            is_box = data.tile_properties.get(gid, {}).get('type') == 'Box'
            if is_box and layer.name != 'boxes':
                raise ValueError(f"Box at ({x}, {y}) must be in the boxes layer")
            if layer.name != 'boxes':
                continue
            if not is_box:
                raise ValueError(f"Tile at ({x}, {y}) in boxes must have type Box")
            if not (0 <= x < data.width and 0 <= y < data.height):
                raise ValueError(f"Box at ({x}, {y}) is outside the map")
            if data.layernames['walls'].data[y][x]:
                raise ValueError(f"Box at ({x}, {y}) overlaps a wall")
            if (x, y) in spawn_positions:
                raise ValueError(f"Box at ({x}, {y}) overlaps Spawn")
            boxes.append((x, y, gid))
    return tuple(boxes)


# =================================================================
# QUEST SCENE
#
# Loads tilemap layers and renders them in the correct order:
# map tiles first, then the player sprite on top.
# =================================================================

class QuestScene(pygamejr.Scene):
    def __init__(self, tilemap):
        super().__init__()
        self._initial_boxes = _get_initial_boxes(tilemap)
        self.initial_box_positions = tuple((x, y) for x, y, gid in self._initial_boxes)
        self.box_sprites = {}
        self._tilemap = tilemap
        # Temporarily set this scene as current so that ImageSprite
        # objects created inside get_layer_sprites() auto-add here.
        previous_scene = pygamejr.get_current_scene()
        pygamejr.set_scene(self)
        try:
            for layer in tilemap.tmxdata.layers:
                if layer.name == 'boxes':
                    continue
                if hasattr(layer, 'tiles'):
                    sprites = tilemap.get_layer_sprites(layer.name)
                    self.add_sprite_list(layer.name, Group(sprites))
            # Clear DEFAULT_LAYER — tile sprites now live in named layer groups.
            self._name_mapping[DEFAULT_LAYER].empty()
            self.add_sprite_list('boxes', Group())
            self._reset_boxes()
        finally:
            pygamejr.set_scene(previous_scene)

    @property
    def box_positions(self):
        return frozenset(self.box_sprites)

    def _clear_boxes(self):
        for sprite in self.box_sprites.values():
            sprite.kill()
        self.box_sprites.clear()

    def _reset_boxes(self):
        self._clear_boxes()
        for x, y, gid in self._initial_boxes:
            sprite = pygamejr.ImageSprite(
                image=self._tilemap.tmxdata.get_tile_image_by_gid(gid),
                crop_alpha=False,
                scene=self,
            )
            self.remove(sprite)
            sprite.rect.topleft = (x * TILE_SIZE, y * TILE_SIZE)
            self.get_sprite_list('boxes').add(sprite)
            self.box_sprites[(x, y)] = sprite

    def _move_box(self, source, destination):
        """Keep current coordinates and rendering together; leave TMX unchanged."""
        if destination in self.box_sprites:
            raise ValueError(f"A box already occupies {destination}")
        sprite = self.box_sprites.pop(source)
        sprite.rect.topleft = (destination[0] * TILE_SIZE, destination[1] * TILE_SIZE)
        self.box_sprites[destination] = sprite

    def draw(self, draw_rect=False):
        # Draw tilemap layers first, then player (DEFAULT_LAYER) on top.
        for name, sprite_list in self._name_mapping.items():
            if name == DEFAULT_LAYER:
                continue
            for sprite in sprite_list:
                sprite.draw(draw_rect=draw_rect)
        for sprite in self._name_mapping[DEFAULT_LAYER]:
            sprite.draw(draw_rect=draw_rect)


# =================================================================
# Build initial scene and set it before creating Player,
# so Player auto-adds to quest_scene's DEFAULT_LAYER.
# =================================================================

quest_scene = QuestScene(tilemap)
pygamejr.set_scene(quest_scene)

win_position = _get_win_position()


class Player(BaseSprite):
    def __init__(self, *args):
        super().__init__(*args)
        self._direction: Direction = Direction.RIGHT
        self._update_image()
        self.rect = self.image.get_rect()
        tile_x, tile_y = _get_spawn_position()
        self.set_position_by_tile(tile_x, tile_y)
        self._is_end = False
        self._is_win_state = False
        self._is_game_over_state = False
        self._on_complete = None
        pygamejr.next_frame()

    @property
    def is_finished(self):
        return self._is_end

    @property
    def is_win(self):
        return self._is_win_state

    @property
    def is_game_over(self):
        return self._is_game_over_state

    @property
    def on_complete(self):
        return self._on_complete

    @on_complete.setter
    def on_complete(self, callback):
        self._on_complete = callback

    def reset(self):
        quest_scene._reset_boxes()
        self._is_end = False
        self._is_win_state = False
        self._is_game_over_state = False
        self._direction = Direction.RIGHT
        self.set_position_by_tile(*_get_spawn_position())
        self._update_image()
        pygamejr.next_frame()

    def set_position_by_tile(self, x, y):
        self._tile_x = x
        self._tile_y = y
        self.rect.centerx = self._tile_x * TILE_SIZE + TILE_SIZE / 2
        self.rect.centery = self._tile_y * TILE_SIZE + TILE_SIZE / 2

    def _update_image(self):
        if self._direction == Direction.RIGHT and CHARACTER_TILES['right']:
            tiles = CHARACTER_TILES['right']
        elif self._direction == Direction.LEFT and CHARACTER_TILES['left']:
            tiles = CHARACTER_TILES['left']
        elif self._direction == Direction.TOP and CHARACTER_TILES['top']:
            tiles = CHARACTER_TILES['top']
        else:
            tiles = CHARACTER_TILES['bottom']
        self.images = [load_image(*tile) for tile in tiles]
        self.image = self.images[0]

    def turn_right(self):
        direction_index = directions.index(self._direction)
        self._direction = directions[(direction_index + 1) % len(directions)]
        self._update_image()
        pygamejr.next_frame()

    def turn_left(self):
        direction_index = directions.index(self._direction)
        self._direction = directions[(direction_index - 1) % len(directions)]
        self._update_image()
        pygamejr.next_frame()

    def _move_top(self):
        self._direction = Direction.TOP
        self._move_to(self._tile_x, self._tile_y - 1)

    def _move_right(self):
        self._direction = Direction.RIGHT
        self._move_to(self._tile_x + 1, self._tile_y)

    def _move_bottom(self):
        self._direction = Direction.BOTTOM
        self._move_to(self._tile_x, self._tile_y + 1)

    def _move_left(self):
        self._direction = Direction.LEFT
        self._move_to(self._tile_x - 1, self._tile_y)

    def is_box_ahead(self) -> bool:
        """Read whether the adjacent cell contains a box, even after completion."""
        dx, dy = {
            Direction.TOP: (0, -1),
            Direction.RIGHT: (1, 0),
            Direction.BOTTOM: (0, 1),
            Direction.LEFT: (-1, 0),
        }[self._direction]
        tile_x, tile_y = self._tile_x + dx, self._tile_y + dy
        return (self._is_inside_map(tile_x, tile_y)
                and (tile_x, tile_y) in quest_scene.box_positions)

    def move_forward(self):
        if self._direction == Direction.TOP:
            self._move_top()
        elif self._direction == Direction.RIGHT:
            self._move_right()
        elif self._direction == Direction.BOTTOM:
            self._move_bottom()
        else:
            self._move_left()

    def _move_to(self, tile_x: int, tile_y: int):
        if self._is_end:
            return

        dx = tile_x - self._tile_x
        dy = tile_y - self._tile_y

        if self._is_wall(tile_x, tile_y) or (tile_x, tile_y) in quest_scene.box_positions:
            self._animate_game_over(dx, dy)
            self._is_end = True
            self._is_game_over_state = True
            if self._on_complete:
                self._on_complete(False)
            return

        character_tiles_count = len(self.images)
        # Scene draws each frame automatically after the yield in every_frame().
        for i, dt in enumerate(pygamejr.every_frame(TILE_SIZE)):
            self.rect.x += dx
            self.rect.y += dy
            self.image = self.images[int((i // (TILE_SIZE / 6)) % character_tiles_count)]

        self.image = self.images[0]

        if self._is_win(tile_x, tile_y):
            self._animate_win()
            self._is_end = True
            self._is_win_state = True
            if self._on_complete:
                self._on_complete(True)

        self._tile_x = tile_x
        self._tile_y = tile_y

    def _is_inside_map(self, tile_x: int, tile_y: int) -> bool:
        return 0 <= tile_x < tilemap.tmxdata.width and 0 <= tile_y < tilemap.tmxdata.height

    def _is_wall(self, tile_x: int, tile_y: int):
        if not self._is_inside_map(tile_x, tile_y):
            return True
        return tilemap.tmxdata.layernames['walls'].data[tile_y][tile_x] != 0

    def _is_win(self, tile_x: int, tile_y: int):
        return tile_x == win_position[0] and tile_y == win_position[1]

    def _animate_game_over(self, dx: float, dy: float):
        old_x = self.rect.x
        old_y = self.rect.y
        max_delta = TILE_SIZE / 5
        # Finite shake animation: 5 cycles.
        for _ in range(5):
            if pygamejr.is_quit():
                break
            delta = 0
            for dt in pygamejr.every_frame(int(max_delta) * 2):
                if delta > max_delta:
                    self.rect.x = old_x
                    self.rect.y = old_y
                    delta = 0
                else:
                    self.rect.x += dx
                    self.rect.y += dy
                    delta += 1
        self.rect.x = old_x
        self.rect.y = old_y

    def _scale_surface(self, surf, scale: float):
        width = round(surf.get_width() * scale)
        height = round(surf.get_height() * scale)
        return pygame.transform.smoothscale(surf, (width, height))

    def _animate_win(self):
        # Temporarily change self.image each frame — scene draws it automatically.
        scale = 1
        original_image = self.images[0]
        for d_scale in [0.01, -0.01] * 10:
            if pygamejr.is_quit():
                break
            for dt in pygamejr.every_frame(30):
                scale += d_scale
                self.image = self._scale_surface(original_image, scale)
        self.image = original_image


player = Player()


def set_map(map):
    '''
    Sets the map.
    :param str map: map path, e.g. codomir.maps.linear.map1
    '''
    global tilemap, quest_scene, win_position, CHARACTER_TILES

    new_tilemap = pygamejr.TileMap(map)
    new_scene = QuestScene(new_tilemap)
    tilemap = new_tilemap
    CHARACTER_TILES = {
        'right':  json.loads(tilemap.tmxdata.properties['character_right'])  if 'character_right'  in tilemap.tmxdata.properties else None,
        'bottom': json.loads(tilemap.tmxdata.properties['character_bottom']) if 'character_bottom' in tilemap.tmxdata.properties else None,
        'left':   json.loads(tilemap.tmxdata.properties['character_left'])   if 'character_left'   in tilemap.tmxdata.properties else None,
        'top':    json.loads(tilemap.tmxdata.properties['character_top'])    if 'character_top'    in tilemap.tmxdata.properties else None,
    }

    old_scene = quest_scene
    quest_scene = new_scene
    old_scene._clear_boxes()

    # Move player from old scene to new scene.
    old_scene.remove(player)
    quest_scene.add(player)
    pygamejr.set_scene(quest_scene)

    player.set_position_by_tile(*_get_spawn_position())
    player._direction = Direction.RIGHT
    player._update_image()
    player._is_end = False
    player._is_win_state = False
    player._is_game_over_state = False
    win_position = _get_win_position()
    pygamejr.next_frame()


def init(src):
    set_map(src)


__all__ = [
    player,
    init,
    set_map,
]
