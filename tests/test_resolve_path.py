"""Tests for resource path resolution helpers."""
from pathlib import Path

from pygamejr.resources.resolve_path import (
    RESOURCE_PATH,
    resolve_path as pygamejr_resolve_path,
)
from codomir.resources.resolve_path import (
    RESOURCE_PATH as CODOMIR_RESOURCE_PATH,
    resolve_path as codomir_resolve_path,
)


def test_pygamejr_resource_path_is_directory():
    assert RESOURCE_PATH.is_dir()
    assert RESOURCE_PATH.name == "resources"


def test_pygamejr_resolve_path_returns_absolute_path():
    p = pygamejr_resolve_path("images/enemies/bee.png")
    assert isinstance(p, Path)
    assert p.is_absolute()
    assert p == RESOURCE_PATH / "images/enemies/bee.png"


def test_pygamejr_resolve_path_accepts_path_input():
    p = pygamejr_resolve_path(Path("images") / "enemies" / "bee.png")
    assert p.is_absolute()
    assert p.name == "bee.png"


def test_pygamejr_resolve_path_does_not_require_existing_file():
    """Helper just performs path math; it must not raise for a missing file."""
    p = pygamejr_resolve_path("does/not/exist.png")
    assert p.is_absolute()
    assert not p.exists()


def test_codomir_resource_path_is_directory():
    assert CODOMIR_RESOURCE_PATH.is_dir()
    assert CODOMIR_RESOURCE_PATH.name == "resources"


def test_codomir_resolve_path_points_inside_codomir_resources():
    p = codomir_resolve_path("kenney_sokoban/map1.tmx")
    assert p.is_absolute()
    assert p.is_file()
    assert CODOMIR_RESOURCE_PATH in p.parents
