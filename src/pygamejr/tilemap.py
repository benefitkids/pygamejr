import os
from pathlib import Path

from pygame.sprite import Sprite as PygameSprite
from pygame import Rect
from pytmx.util_pygame import load_pygame, pygame_image_loader

from .sprite.image import ImageSprite


# def get_tile_by_local_id(tmx_data, local_id, tileset_name=None):
#     """
#     tileset_name: Имя набора тайлов (как в Tiled)
#     local_id: Номер картинки внутри набора (0, 1, 2...)
#     """
#     # Ищем нужный тайлсет
#     target_tileset = None
#     # for ts in tmx_data.tilesets:
#     #     if ts.name == tileset_name:
#     #         target_tileset = ts
#     #         break
#     target_tileset = tmx_data.tilesets[0]
#
#     if target_tileset:
#         # Вычисляем настоящий GID
#         real_gid = target_tileset.firstgid + local_id
#
#         # Теперь это сработает, так как load_all_tiles загрузил картинку
#         return tmx_data.get_tile_image_by_gid(real_gid)
#
#     return None

# Судя по всему в pytmx есть ошибка, опция load_all_tiles не работает.
# Воркэраунд под эту ошибку.
# tmxdata.gidmap = {}
# tmxdata.reload_images()
def load_image(tilemap, row, col):
    tileset = tilemap.tilesets[0]
    colorkey = getattr(tileset, "trans", None)
    path = os.path.join(os.path.dirname(tilemap.filename), tileset.source)
    loader = pygame_image_loader(path, colorkey, tileset=tileset)

    # tileset = None
    # for ts in tmx_data.tilesets:
    #     if ts.name == tileset_name:
    #         tileset = ts
    #         break
    # tileset = tilemap.tilesets[0]
    # source_image = getattr(tileset, 'image', None)
    # if not source_image:
    #     print(f"Изображение для не загружено.")
    #     return None

    # 3. Математика координат (учитываем отступы margin и spacing)
    tw = tileset.tilewidth
    th = tileset.tileheight
    margin = tileset.margin
    spacing = tileset.spacing

    # Количество колонок в тайлсете
    # image_width - margin * 2 + spacing... упрощенно:
    width_pixel = tileset.width
    columns = (width_pixel - margin) // (tw + spacing)

    # Вычисляем координаты пикселей
    x = margin + col * (tw + spacing)
    y = margin + row * (th + spacing)

    rect = Rect(x, y, tw, th)
    return loader(rect, None)

class TileMap:
    def __init__(
            self,
            map_file: str | Path,
    ) -> None:
        self.tmxdata = load_pygame(map_file, image_loader=pygame_image_loader, load_all_tiles=True)

    def get_layer_sprites(self, layer_name: str) -> list[PygameSprite]:
        sprites = []
        layer = self.tmxdata.get_layer_by_name(layer_name)

        for x, y, image in layer.tiles():
            sprite = ImageSprite(image=image, crop_alpha=False)
            sprite.rect.x = x * self.tmxdata.tilewidth
            sprite.rect.y = y * self.tmxdata.tileheight
            sprites.append(sprite)

        return sprites

    def get_sprite_by_tileset_position(self, row, col) -> ImageSprite:
        # image = self.tmxdata.get_tile_image_by_gid(gid)
        image = load_image(self.tmxdata, row, col)
        return ImageSprite(image=image)
