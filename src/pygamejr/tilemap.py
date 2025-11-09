from pathlib import Path

from pytmx.util_pygame import load_pygame, pygame_image_loader

class TileMap:
    def __init__(
            self,
        map_file: str | Path,
    ) -> None:
