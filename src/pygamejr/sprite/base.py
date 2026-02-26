from math import sin, cos, radians
import pygame
from ..base import screen, get_current_scene

# GLOBAL VARIABLES
COLOR = (255, 100, 98)
SURFACE_COLOR = (167, 255, 100)
WIDTH = 500
HEIGHT = 500


class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, sprite_angle: float = 0, visible: bool = True, *args):
        super().__init__(*args)
        self._is_visible = visible
        self._sprite_angle = sprite_angle
        self._angle = sprite_angle
        get_current_scene().add(self)

    def __del__(self):
        self.kill()

    @property
    def is_visible(self):
        return self._is_visible

    @is_visible.setter
    def is_visible(self, value):
        self._is_visible = value

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
