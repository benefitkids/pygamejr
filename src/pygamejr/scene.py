from pygame.sprite import Sprite as PygameSprite, AbstractGroup, Group
from .tilemap import TileMap

DEFAULT_LAYER = "default"

class Scene:
    def __init__(self):
        self._name_mapping: dict[str, AbstractGroup] = {
            DEFAULT_LAYER: Group()
        }

    @classmethod
    def from_tilemap(cls, tilemap: TileMap) -> "Scene":
        from .base import get_current_scene, set_scene

        scene = cls()
        previous_scene = get_current_scene()  # may be None
        set_scene(scene)

        for layer in tilemap.tmxdata.layers:
            if hasattr(layer, 'tiles'):
                sprites = tilemap.get_layer_sprites(layer.name)
                scene.add_sprite_list(name=layer.name, sprite_list=Group(sprites))

        scene._name_mapping[DEFAULT_LAYER].empty()
        set_scene(previous_scene)
        return scene

    def add(self, sprite: PygameSprite) -> None:
        self._name_mapping[DEFAULT_LAYER].add(sprite)

    def remove(self, sprite: PygameSprite) -> None:
        self._name_mapping[DEFAULT_LAYER].remove(sprite)

    def add_sprite_list(self, name: str, sprite_list: AbstractGroup) -> None:
        self._name_mapping[name] = sprite_list

    def get_sprite_list(self, name: str) -> AbstractGroup | None:
        return self._name_mapping.get(name)

    def update(self, dt: float = 0) -> None:
        for sprite_list in self._name_mapping.values():
            sprite_list.update(dt)

    def draw(self, draw_rect: bool = False) -> None:
        for sprite_list in self._name_mapping.values():
            for sprite in sprite_list:
                sprite.draw(draw_rect=draw_rect)
