import pathlib
import pygame
from .base import BaseSprite


def _crop_alpha(surface):
    """
    Обрезает прозрачные области вокруг изображения.
    Возвращает новый Surface, содержащий только видимую часть.
    """
    rect = surface.get_bounding_rect()
    cropped = surface.subsurface(rect)
    # Делаем копию, чтобы получить независимый Surface
    return cropped.copy()


class ImageSprite(BaseSprite):
    def __init__(
            self,
            filename: str | pathlib.Path = None,
            image: pygame.Surface = None,
            sprite_angle: float = 0,
            crop_alpha: bool = True,
            *args):
        super().__init__(sprite_angle, *args)
        if filename:
            self._original_image = pygame.image.load(filename).convert_alpha()
        else:
            self._original_image = image
        if crop_alpha:
            self._original_image = _crop_alpha(self._original_image)
        self.image = self._original_image
        self.rect = self.image.get_frect()
        self.mask = pygame.mask.from_surface(self.image)

    def rotate(self, angle: float):
        super().rotate(angle)
        self.image = pygame.transform.rotate(self._original_image, self._angle)
        self.rect = self.image.get_frect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def turn_left(self, angle: float = 1):
        self.rotate(-angle)

    def turn_right(self, angle: float = 1):
        self.rotate(angle)
