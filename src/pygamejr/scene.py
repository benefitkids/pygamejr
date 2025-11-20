from pygame.sprite import Sprite as PygameSprite, AbstractGroup
from .tilemap import TileMap

class Scene:
    def __init__(self):
        self._sprite_lists: list[AbstractGroup | PygameSprite] = []
        self._name_mapping: dict[str, AbstractGroup | PygameSprite] = {}

    @classmethod
    def from_tilemap(cls, tilemap: TileMap) -> "Scene":
        scene = cls()
        for name, sprite_list in tilemap.sprite_lists.items():
            scene.add_sprite_list(name=name, sprite_list=sprite_list)
        return scene

    def add_sprite_list(self, name: str, sprite_list: PygameSprite) -> None:
        self._name_mapping[name] = sprite_list
        self._sprite_lists.append(sprite_list)

    def draw(self) -> None:
        for sprite_list in self._sprite_lists:
            for sprite in sprite_list:
                sprite.draw()
