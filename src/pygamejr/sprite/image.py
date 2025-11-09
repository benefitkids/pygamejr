import pygame
from .base import BaseSprite


class ImageSprite(BaseSprite):
    def __init__(self, filename, sprite_angle: float = 0, *args):
        super().__init__(sprite_angle,*args)
        self._original_image = pygame.image.load(filename).convert_alpha()
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
