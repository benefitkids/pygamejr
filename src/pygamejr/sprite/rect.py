import pygame
from .base import BaseSprite

# GLOBAL VARIABLES
COLOR = (255, 100, 98)


class RectSprite(BaseSprite):
    def __init__(self, color="red", width=50, height=50, x=0, y=0):
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.set_colorkey(COLOR)
        pygame.draw.rect(self.image,
                           color,
                           pygame.FRect((x, y, width, height)),
        )

        self.rect = self.image.get_frect()
