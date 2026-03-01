import pygame
from .base import BaseSprite

# GLOBAL VARIABLES
COLOR = (255, 100, 98)


class RectSprite(BaseSprite):
    def __init__(
            self,
            color="red",
            width=50,
            height=50,
            x=0,
            y=0,
            sprite_angle: float = 0,
            scene=None,
            *args
    ):
        super().__init__(sprite_angle, scene=scene, *args)

        self.image = pygame.Surface([width, height])
        self.image.set_colorkey(COLOR)
        pygame.draw.rect(self.image,
                           color,
                           pygame.FRect((x, y, width, height)),
        )

        self.rect = self.image.get_frect()
