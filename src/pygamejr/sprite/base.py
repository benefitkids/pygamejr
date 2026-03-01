from math import sin, cos, radians
import pygame
from ..base import screen, get_current_scene, get_global_scene

# GLOBAL VARIABLES
COLOR = (255, 100, 98)
SURFACE_COLOR = (167, 255, 100)
WIDTH = 500
HEIGHT = 500


class BaseSprite(pygame.sprite.DirtySprite):
    def __init__(self, sprite_angle: float = 0, is_visible: bool = True, scene=None, *args):
        super().__init__(*args)
        super()._set_visible(1 if is_visible else 0)
        self._sprite_angle = sprite_angle
        self._angle = sprite_angle
        (scene or get_current_scene() or get_global_scene()).add(self)

    def __del__(self):
        self.kill()

    @property
    def is_visible(self):
        return bool(self.visible)

    @is_visible.setter
    def is_visible(self, value):
        self.visible = 1 if value else 0

    def draw(self, draw_rect: bool = False):
        if self.is_visible:
            screen.blit(self.image, self.rect)
            if draw_rect:
                pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)

    def move_forward(self, distance: float = 1.0):
        self.rect.x += distance * sin(radians(self._angle))
        self.rect.y += distance * cos(radians(self._angle))

    def rotate(self, angle: float):
        self._angle += angle
        self._angle %= 360
