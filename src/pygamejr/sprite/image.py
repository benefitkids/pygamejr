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


def _make_original_surface(
    filename: str | pathlib.Path | None,
    image: pygame.Surface | str | pathlib.Path | None,
    crop_alpha: bool,
) -> pygame.Surface:
    if filename:
        surf = pygame.image.load(filename).convert_alpha()
    elif image is not None:
        if isinstance(image, pygame.Surface):
            surf = image
        else:
            surf = pygame.image.load(image).convert_alpha()
    else:
        raise ValueError("ImageSprite requires either filename or image")
    if crop_alpha:
        surf = _crop_alpha(surf)
    return surf


class ImageSprite(BaseSprite):
    def __init__(
            self,
            filename: str | pathlib.Path = None,
            image: pygame.Surface = None,
            crop_alpha: bool = True,
            sprite_angle: float = 0,
            scene=None,
            *args):
        super().__init__(sprite_angle, scene=scene, *args)
        self._original_image = _make_original_surface(filename, image, crop_alpha)
        self._sync_display_image(preserve_center=False)

    def _sync_display_image(self, preserve_center: bool):
        self.image = pygame.transform.rotate(self._original_image, self._angle)
        if preserve_center:
            self.rect = self.image.get_frect(center=self.rect.center)
        else:
            self.rect = self.image.get_frect()
        self.mask = pygame.mask.from_surface(self.image)

    def set_image(
            self,
            filename: str | pathlib.Path = None,
            image: pygame.Surface = None,
            crop_alpha: bool = True):
        """
        Replace the sprite texture. Preserves rect center and applies current rotation.
        Pass either filename or image, the same as for the constructor.
        """
        self._original_image = _make_original_surface(filename, image, crop_alpha)
        self._sync_display_image(preserve_center=True)

    def rotate(self, angle: float):
        super().rotate(angle)
        self._sync_display_image(preserve_center=True)

    def turn_left(self, angle: float = 1):
        self.rotate(-angle)

    def turn_right(self, angle: float = 1):
        self.rotate(angle)
