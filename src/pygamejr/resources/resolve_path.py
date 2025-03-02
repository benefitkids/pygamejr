from typing import Union
from pathlib import Path

#: The absolute path to this directory
RESOURCE_PATH = Path(__file__).parent.absolute()


def resolve_path(path: Union[str, Path]) -> Path:
    path = Path(RESOURCE_PATH / path)
    return path.absolute()
