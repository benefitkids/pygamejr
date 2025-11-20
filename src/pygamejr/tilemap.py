from pathlib import Path

from pygame.sprite import Sprite as PygameSprite
from pytmx.util_pygame import load_pygame, pygame_image_loader

from .sprite.image import ImageSprite


class TileMap:
    def __init__(
            self,
            map_file: str | Path,
    ) -> None:
        self.tmxdata = load_pygame(map_file, image_loader=pygame_image_loader)

    def get_layer_sprites(self, layer_name: str) -> list[PygameSprite]:
        sprites = []
        layer = self.tmxdata.get_layer_by_name(layer_name)

        for x, y, image in layer.tiles():
            sprite = ImageSprite(image=image)
            sprite.rect.x = x * self.tmxdata.tilewidth
            sprite.rect.y = y * self.tmxdata.tileheight
            sprites.append(sprite)

        return sprites
