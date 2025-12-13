import time
import pygame
from .text import TextSprite

# GLOBAL VARIABLES
COLOR = (255, 100, 98)
SURFACE_COLOR = (167, 255, 100)
WIDTH = 500
HEIGHT = 500


class SubtitlesSprite(TextSprite):
    def __init__(self, text_list: list[str] = [], size: int = 32, color=(255, 255, 255), font_name=None,
                 sprite_angle: float = 0,
                 *args):
        super().__init__(text_list[0], size, color, font_name, sprite_angle, *args)
        self.is_visible = False
        self._text_list = text_list
        self._text_index = 0
        self._last_update = time.time()

    @property
    def is_visible(self):
        return self._is_visible

    @is_visible.setter
    def is_visible(self, value):
        if value != self._is_visible:
            self._is_visible = value
            if value:
                self._last_update = time.time()
                self._render_text()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if self._text != value:
            self._text = value
            self._render_text()

    def update(self):
        if not self.is_visible:
            return

        current_time = time.time()
        if current_time - self._last_update > 3:
            print(self._text_index, len(self._text_list))
            if self._text_index >= len(self._text_list) - 1:
                self._text_index = 0
                self.is_visible = False
            else:
                self._text_index += 1
                self.text = self._text_list[self._text_index]
                self._render_text()
            self._last_update = current_time
