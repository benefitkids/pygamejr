import pygame
from .base import BaseSprite


class ImageSprite(BaseSprite):
    def __init__(self, filename):
        super().__init__()
        self.image = pygame.image.load(filename).convert_alpha()
        self.rect = self.image.get_rect()
