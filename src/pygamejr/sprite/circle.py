import pygame
from .base import BaseSprite

# GLOBAL VARIABLES
COLOR = (255, 100, 98)
SURFACE_COLOR = (167, 255, 100)
WIDTH = 500
HEIGHT = 500


class CircleSprite(BaseSprite):
    def __init__(
            self,
            color="red",
            radius=50,
            sprite_angle: float = 0,
            scene=None,
            *args):
        super().__init__(sprite_angle, scene=scene, *args)

        self.image = pygame.Surface([radius*2, radius*2])
        self.image.set_colorkey(COLOR)
        pygame.draw.circle(self.image,
                           color,
                           pygame.Vector2(radius, radius),
                           radius
        )

        self.rect = self.image.get_frect()
