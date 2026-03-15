# pygamejr

A simple PyGame extension library for educational game development.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

> [Русская документация](README_RU.md)

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [API Reference — pygamejr](#api-reference--pygamejr)
  - [Game Loop](#game-loop)
  - [Scene Management](#scene-management)
  - [Sprites](#sprites)
  - [Resources](#resources)
  - [TileMap](#tilemap)
- [API Reference — codomir](#api-reference--codomir)
  - [Player](#player)
  - [Maps](#maps)
- [Examples](#examples)
- [Project Structure](#project-structure)

---

## Overview

`pygamejr` is a thin wrapper around [pygame-ce](https://pyga.me/) designed for teaching programming to beginners.
It provides two installable packages:

| Package | Description |
|---------|-------------|
| `pygamejr` | Core engine: sprites, scenes, game loop |
| `codomir` | Quest/map layer: tile-based character movement on `.tmx` maps |

---

## Installation

```bash
# Clone the repository
git clone https://github.com/benefitkids/pygamejr.git
cd pygamejr

# Install in editable mode
pip install -e .
```

**Dependencies** (installed automatically):
- `pygame-ce` — community edition of pygame
- `pytmx` — loader for Tiled `.tmx` map files

---

## Quick Start

### Minimal example

```python
import pygamejr

bee = pygamejr.ImageSprite(pygamejr.resources.image.bee)
pygamejr.wait_quit()
```

### Quest game (codomir)

```python
from codomir import player, wait_quit

player.move_forward()
player.turn_right()
player.move_forward()
wait_quit()
```

### Run the demos

```bash
python demo/1simple.py
python demo/scene.py
python demo/codomir/loop/map1.py
```

---

## Architecture

```
pygamejr/
├── pygamejr/          # core engine
│   ├── base.py        # pygame init, screen, game loop, scene switching
│   ├── scene.py       # Scene — named sprite group container
│   ├── tilemap.py     # TileMap — pytmx wrapper
│   ├── sprite/        # sprite classes
│   │   ├── base.py    # BaseSprite
│   │   ├── image.py   # ImageSprite
│   │   ├── text.py    # TextSprite
│   │   ├── circle.py  # CircleSprite
│   │   ├── rect.py    # RectSprite
│   │   └── subtitles.py  # SubtitlesSprite
│   └── resources/     # bundled images and path resolver
└── codomir/           # quest/map layer
    ├── quest.py       # QuestScene, Player, Direction
    ├── maps/          # .tmx map path constants
    └── resources/     # codomir-specific assets
```

### Two-scene system

Every running game has two simultaneous scenes:

- **Global scene** — always rendered on top; holds HUD elements that survive level transitions.
  Sprites added _before_ the first `set_scene()` call go here automatically.
- **Current scene** — the active gameplay scene; switched with `set_scene()`.
  Sprites added _after_ `set_scene()` go here automatically.

### Import-time side effects

Importing `pygamejr` calls `pygame.init()` and creates the window immediately.
Importing `codomir` additionally loads the default map, builds the scene, and creates the `player` singleton.

---

## API Reference — pygamejr

### Game Loop

#### `every_frame(frame_count=0, draw_sprites_rect=False)`

Generator that drives the main game loop at 60 fps.
Yields `dt` (delta time in seconds) each frame.
Processes all pygame events and renders sprites automatically.

```python
for dt in pygamejr.every_frame():
    sprite.rect.x += 100 * dt   # frame-rate-independent movement
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `frame_count` | `0` | Stop after N frames (0 = infinite) |
| `draw_sprites_rect` | `False` | Draw collision rectangles for debugging |

#### `wait_quit()`

Blocks until the user closes the window.

#### `next_frame()`

Renders exactly one frame (used internally by `codomir` for tile animations).

#### `is_quit() -> bool`

Returns `True` if a quit event has been received.

---

### Scene Management

#### `set_scene(scene: Scene)`

Sets the active scene. Calls `scene.init_scene()` and clears sprite auto-registration target.

#### `get_current_scene() -> Scene | None`

Returns the current (gameplay) scene.

#### `get_global_scene() -> Scene`

Returns the global (HUD) scene, creating it on first call.

---

### `Scene`

Container for named sprite groups.

```python
scene = pygamejr.Scene()
```

| Method | Description |
|--------|-------------|
| `add(sprite)` | Add sprite to the `"default"` layer |
| `remove(sprite)` | Remove sprite from the `"default"` layer |
| `add_sprite_list(name, group)` | Register a named `LayeredUpdates` group |
| `get_sprite_list(name) -> LayeredUpdates` | Retrieve a named group |
| `update(dt)` | Update all groups |
| `draw(draw_rect=False)` | Draw all groups; `draw_rect=True` shows rects |
| `init_scene()` | Called when scene becomes active (override this) |
| `Scene.from_tilemap(tilemap)` | Class method — build scene from a `TileMap` |

---

### Sprites

All sprites auto-register to the current (or global) scene on creation.
Pass `scene=` to override registration.

#### `BaseSprite`

```python
pygamejr.sprite.BaseSprite(sprite_angle=0, is_visible=True, scene=None)
```

| Property/Method | Description |
|-----------------|-------------|
| `rect` | `pygame.Rect` — position and size |
| `is_visible` | Show/hide sprite |
| `move_forward(distance=1.0)` | Move in direction of `sprite_angle` |
| `rotate(angle)` | Rotate by `angle` degrees |

#### `ImageSprite`

```python
pygamejr.ImageSprite(filename=None, image=None, crop_alpha=True,
                     sprite_angle=0, scene=None)
```

Loads an image from a file path or `pygame.Surface`.
Automatically crops transparent borders and creates a pixel-perfect mask for collision.

```python
bee = pygamejr.ImageSprite(pygamejr.resources.image.bee)
bee.rect.center = (400, 300)
```

| Parameter | Description |
|-----------|-------------|
| `filename` | Path to image file |
| `image` | `pygame.Surface` to use directly |
| `crop_alpha` | Crop transparent border (default `True`) |

| Method | Description |
|--------|-------------|
| `rotate(angle)` | Rotate image and update collision mask |
| `turn_left(angle=1)` | Rotate counter-clockwise |
| `turn_right(angle=1)` | Rotate clockwise |

#### `TextSprite`

```python
pygamejr.TextSprite(text='', size=32, color=(255, 255, 255),
                    font_name=None, sprite_angle=0, scene=None)
```

Renders text as a sprite. Changing the `.text` property re-renders automatically.

```python
label = pygamejr.TextSprite("Score: 0", size=24, color=(255, 255, 0))
label.text = "Score: 10"   # updates automatically
```

#### `CircleSprite`

```python
pygamejr.CircleSprite(color="red", radius=50, sprite_angle=0, scene=None)
```

#### `RectSprite`

```python
pygamejr.RectSprite(color="red", width=50, height=50,
                    x=0, y=0, sprite_angle=0, scene=None)
```

#### `SubtitlesSprite`

Scrolling text overlay — cycles through a list of strings every 3 seconds, then hides.

```python
pygamejr.sprite.SubtitlesSprite(
    text_list=["Hello!", "Welcome to the game."],
    size=28, color=(255, 255, 255)
)
```

---

### Resources

#### `pygamejr.resources.image`

Module of named constants for built-in images.

```python
pygamejr.resources.image.bee
pygamejr.resources.image.coin_gold
pygamejr.resources.image.player_ship1_orange
pygamejr.resources.image.meteor_grey_big1
```

**Categories:**

| Category | Examples |
|----------|---------|
| Creatures | `bee`, `fly`, `frog`, `ladybug`, `mouse`, `worm_green` |
| Enemies | `slime_blue`, `slime_green`, `saw`, `fish_swim1` |
| Items | `coin_gold`, `gem_blue`, `key_gold`, `star_gold` |
| Space shooter | `player_ship1_orange`, `laser_blue01`, `meteor_grey_big1` |
| UI | `flag_green1`, `ladder_mid`, `lives` |

---

### TileMap

```python
tilemap = pygamejr.TileMap("path/to/map.tmx")
sprites = tilemap.get_layer_sprites("Ground")
```

| Method | Description |
|--------|-------------|
| `get_layer_sprites(layer_name)` | Returns `list[ImageSprite]` for named tile layer |
| `tmxdata` | Raw `pytmx` data object |

---

## API Reference — codomir

### Player

The `player` singleton is created automatically on `import codomir`.

```python
from codomir import player, wait_quit
```

| Method | Description |
|--------|-------------|
| `player.move_forward()` | Move one tile (64 px) in the current direction with animation |
| `player.turn_left()` | Turn 90° counter-clockwise |
| `player.turn_right()` | Turn 90° clockwise |

The player detects:
- **Walls** — blocks movement, plays shake animation
- **Win tile** — plays win animation and stops

#### `set_map(map_path)` / `init(map_path)`

Load a new `.tmx` map and reposition the player at the spawn tile.

```python
from codomir import set_map, maps

set_map(maps.linear.map2)
```

---

### Maps

```python
from codomir import maps

maps.linear.map1        # linear map 1
maps.linear.map2        # linear map 2
# ...
maps.loop.map_loop1     # loop map 1
maps.pirates.linear.map1
```

**Map collections:**

| Module | Description |
|--------|-------------|
| `maps.linear` | Straight-path maps (map1 – map6) |
| `maps.loop` | Loop maps (map_loop1 – map_loop6) |
| `maps.nested_loops` | Nested loop maps |
| `maps.pirates.linear` | Pirate-themed maps |

---

## Examples

### Simple animation

```python
import pygamejr

bee = pygamejr.ImageSprite(pygamejr.resources.image.bee)
bee.rect.center = (400, 300)

for dt in pygamejr.every_frame():
    bee.move_forward(150 * dt)
```

### Multi-scene game with HUD

```python
import pygamejr
import pygame

# --- Global scene (HUD, always visible) ---
score_label = pygamejr.TextSprite("Score: 0", size=24)
score_label.rect.topleft = (10, 10)

# --- Level 1 ---
level1 = pygamejr.Scene()
pygamejr.set_scene(level1)

enemy = pygamejr.ImageSprite(pygamejr.resources.image.bee)
enemy.rect.center = (400, 300)

score = 0

for dt in pygamejr.every_frame():
    enemy.move_forward(100 * dt)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        score += 1
        score_label.text = f"Score: {score}"
```

### Quest game with custom map

```python
from codomir import player, wait_quit, set_map, maps

set_map(maps.linear.map3)

player.move_forward()
player.move_forward()
player.turn_right()
player.move_forward()

wait_quit()
```

### Tile-based world from .tmx file

```python
import pygamejr

tilemap = pygamejr.TileMap("levels/world.tmx")
scene = pygamejr.Scene.from_tilemap(tilemap)
pygamejr.set_scene(scene)

pygamejr.wait_quit()
```

---

## Project Structure

```
pygamejr/
├── src/
│   ├── pygamejr/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── scene.py
│   │   ├── tilemap.py
│   │   ├── sprite/
│   │   │   ├── base.py
│   │   │   ├── image.py
│   │   │   ├── text.py
│   │   │   ├── circle.py
│   │   │   ├── rect.py
│   │   │   └── subtitles.py
│   │   ├── resources/
│   │   │   ├── image.py
│   │   │   └── resolve_path.py
│   │   └── utils/
│   │       └── screen_size.py
│   └── codomir/
│       ├── __init__.py
│       ├── quest.py
│       ├── maps/
│       │   ├── linear.py
│       │   ├── loop.py
│       │   ├── nested_loops.py
│       │   └── pirates/
│       └── resources/
├── demo/
│   ├── 1simple.py
│   ├── scene.py
│   ├── space_invaders/
│   └── codomir/
├── pyproject.toml
└── README.md
```

---

## Window Configuration

Control window size with environment variables before importing `pygamejr`:

```bash
PYGAMEJR_WINDOW_WIDTH=1024 PYGAMEJR_WINDOW_HEIGHT=768 python my_game.py
```

---

## License

MIT © Alexander Mironov
