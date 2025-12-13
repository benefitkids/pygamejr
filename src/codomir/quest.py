from enum import Enum
import os
import json
import pygame

# TODO: Переименовать в player_sprite.py и часть кода вынести в __init__.py
# from pygamejr.base import window_width

pygame.init()

display_info = pygame.display.Info()
screen_width = display_info.current_w

# https://stackoverflow.com/questions/4135928/pygame-display-position
# import pygame
window_width = 8*64
window_height = 8*64
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (screen_width - window_width, 50)
os.environ['PYGAMEJR_WINDOW_WIDTH'] = f"{window_width}"
os.environ['PYGAMEJR_WINDOW_HEIGHT'] = f"{window_height}"

import pygamejr
from pygamejr.sprite.base import BaseSprite
from .maps.linear import map1

from pytmx.util_pygame import load_pygame, pygame_image_loader

# Инициализипуем display перед тем как загружать картинки.
# Иначе будет ошибка.
# pygamejr.get_screen()
# tmxdata = load_pygame(map1)
tilemap = pygamejr.TileMap(map1)

CHARACTER_TILES = {
    'right': json.loads(tilemap.tmxdata.properties['character_right']) if 'character_right' in tilemap.tmxdata.properties else None,
    'bottom': json.loads(tilemap.tmxdata.properties['character_bottom']) if 'character_bottom' in tilemap.tmxdata.properties else None,
    'left': json.loads(tilemap.tmxdata.properties['character_left']) if 'character_left' in tilemap.tmxdata.properties else None,
    'top': json.loads(tilemap.tmxdata.properties['character_top']) if 'character_top' in tilemap.tmxdata.properties else None,
}

# Судя по всему в pytmx есть ошибка, опция load_all_tiles не работает.
# Воркэраунд под эту ошибку.
# tmxdata.gidmap = {}
# tmxdata.reload_images()
def load_image(tile_x, tile_y):
    ts = tilemap.tmxdata.tilesets[0]
    colorkey = getattr(ts, "trans", None)
    path = os.path.join(os.path.dirname(tilemap.tmxdata.filename), ts.source)
    loader = pygame_image_loader(path, colorkey, tileset=ts)
    rect = (tile_x * ts.tilewidth, tile_y * ts.tileheight, ts.tilewidth, ts.tileheight)
    return loader(rect, None)

def set_map(map):
    '''
    Устанавливает карту.
    :param str map: карта, например "pygamejr.resources.quest.map1"
    '''
    global tilemap
    global win_position
    tilemap = pygamejr.TileMap(map)
    player.set_position_by_tile(*_get_spawn_position())
    win_position = _get_win_position()


# https://stackoverflow.com/questions/4135928/pygame-display-position

TILE_SIZE = 64


class Direction(Enum):
    TOP = 1
    RIGHT = 2
    BOTTOM = 3
    LEFT = 4

directions = (Direction.TOP, Direction.RIGHT, Direction.BOTTOM, Direction.LEFT)

def init(src):
    global tilemap
    tilemap = pygamejr.TileMap(src)

def _blit_all_tiles(window, tmxdata, world_offset):
    for layer in tmxdata:
        for tile in layer.tiles():
            x = tile[0] * TILE_SIZE + world_offset[0]
            y = tile[1] * TILE_SIZE + world_offset[1]
            window.blit(tile[2], (x, y))

def _get_spawn_position():
    return _get_position_by_type('Spawn')

def _get_win_position():
    return _get_position_by_type('Win')

def _get_position_by_type(tile_type):
    for tile in  tilemap.tmxdata.layernames['objects']:
        tile_id = tile[2]
        if tile_id and tilemap.tmxdata.tile_properties[tile_id]['type'] == tile_type:
            return tile[0], tile[1]
    return 0, 0

win_position = _get_win_position()


class Player(BaseSprite):
    def __init__(self, *args):
        super().__init__(*args)
        self._direction = Direction.RIGHT
        self._update_image()
        self.rect = self.image.get_rect()
        tile_x, tile_y = _get_spawn_position()
        self.set_position_by_tile(tile_x, tile_y)
        self._is_end = False
        self.draw()
        pygame.display.flip()

    def set_position_by_tile(self, x, y):
        self._tile_x = x
        self._tile_y = y
        self.rect.centerx = self._tile_x * TILE_SIZE + TILE_SIZE / 2
        self.rect.centery = self._tile_y * TILE_SIZE + TILE_SIZE / 2


    def _update_image(self):
        if self._direction == Direction.RIGHT and CHARACTER_TILES['right']:
            tiles = CHARACTER_TILES['right']
        elif self._direction == Direction.LEFT and CHARACTER_TILES['left']:
            tiles =  CHARACTER_TILES['left']
        elif self._direction == Direction.TOP and CHARACTER_TILES['top']:
            tiles =  CHARACTER_TILES['top']
        else:
            tiles = CHARACTER_TILES['bottom']

        self.images = [load_image(*tile) for tile in tiles]
        self.image = self.images[0]
        # self.rect = self.image.get_rect()

    def turn_right(self):
        direction_index = directions.index(self._direction)
        direction_index = (direction_index + 1) % len(directions)
        self._direction = directions[direction_index]
        self._update_image()
        self.draw()
        pygame.display.flip()

    def turn_left(self):
        direction_index = directions.index(self._direction)
        direction_index = (direction_index - 1) % len(directions)
        self._direction = directions[direction_index]
        self._update_image()
        self.draw()
        pygame.display.flip()

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

        if self._is_wall(tile_x, tile_y):
            self._animate_game_over(dx, dy)
            self._is_end = True
            return

        for i, dt in enumerate(pygamejr.every_frame(TILE_SIZE)):
            self.rect.x += dx
            self.rect.y += dy
            image_index = int((i // (TILE_SIZE / 6)) % 3)
            self.image = self.images[image_index]
            self.draw()

        self.image = self.images[0]
        self.draw()

        if self._is_win(tile_x, tile_y):
            self._animate_win()
            self._is_end = True

        self._tile_x = tile_x
        self._tile_y = tile_y

    def _is_wall(self, tile_x: int, tile_y: int):
        return tilemap.tmxdata.layernames['walls'].data[tile_y][tile_x] != 0

    def _is_win(self, tile_x: int, tile_y: int):
        return tile_x == win_position[0] and tile_y == win_position[1]

    def _animate_game_over(self, dx: float, dy: float):
        old_x = self.rect.x
        old_y = self.rect.y
        max_delta = TILE_SIZE / 5
        delta = 0
        for dt in pygamejr.every_frame():
            if delta > max_delta:
                self.rect.x = old_x
                self.rect.y = old_y
                delta = 0
            else:
                self.rect.x += dx
                self.rect.y += dy
                delta += 1
            self.draw()

    def _scale_surface(self, surf, scale: float):
        width = round(surf.get_width() * scale)
        height = round(surf.get_height() * scale)
        return pygame.transform.smoothscale(surf, (width, height))

    def _animate_win(self):
        scale = 1
        for d_scale in [0.01, -0.01]*10:
            if pygamejr.is_quit():
                break
            for dt in pygamejr.every_frame(30):
                scale += d_scale
                self._draw_map()
                player_surface = self._scale_surface(self.image, scale)
                pygamejr.screen.blit(player_surface, self.rect)

    def draw(self, *args, **kwargs):
        self._draw_map()
        super().draw( *args, **kwargs)

    def _draw_map(self):
        _blit_all_tiles(pygamejr.screen, tilemap.tmxdata, (0, 0))


player = Player()
player.draw()

__all__ = [
    player,
    init,
    set_map
]