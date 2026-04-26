"""Sanity checks for the bundled image resource catalog."""
from pathlib import Path

from pygamejr.resources import image as image_resources


def _public_path_attrs(module):
    """Yield (name, value) pairs for module attributes that look like resource paths."""
    for name in dir(module):
        if name.startswith("_"):
            continue
        value = getattr(module, name)
        if isinstance(value, Path):
            yield name, value


def test_image_module_exposes_resource_paths():
    paths = dict(_public_path_attrs(image_resources))
    assert paths, "image resources module exposes no Path attributes"


def test_advertised_image_files_exist_on_disk():
    """Every image path advertised by ``pygamejr.resources.image`` must exist."""
    missing = [
        f"{name} -> {path}"
        for name, path in _public_path_attrs(image_resources)
        if not path.is_file()
    ]
    assert not missing, "missing resource files: " + ", ".join(missing)


def test_known_resource_aliases():
    assert image_resources.bee.name == "bee.png"
    assert image_resources.coin_silver == image_resources.coin_silver_test
    assert image_resources.coin_gold == image_resources.gold_1
