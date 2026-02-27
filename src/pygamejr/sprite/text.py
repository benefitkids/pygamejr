import pygame
from .base import BaseSprite

# GLOBAL VARIABLES
COLOR = (255, 100, 98)
SURFACE_COLOR = (167, 255, 100)
WIDTH = 500
HEIGHT = 500


class TextSprite(BaseSprite):
    def __init__(self, text: str='', size: int = 32, color=(255, 255, 255), font_name=None, sprite_angle: float = 0,
                 *args):
        super().__init__(sprite_angle, *args)
        self._text = text
        self._size = size
        self._color = color
        self._font = pygame.font.Font(font_name, size)
        self._render_text()

    def _render_text(self):
        try:
            old_topleft = self.rect.topleft
        except AttributeError:
            old_topleft = None
        self._original_image = self._font.render(self._text, True, self._color)
        self.image = self._original_image
        self.rect = self.image.get_frect()
        if old_topleft is not None:
            self.rect.topleft = old_topleft
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if self._text != value:
            self._text = value
            self._render_text()
