# pygamejr

Простая обучающая библиотека расширений для PyGame.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

> [English documentation](README.md)

---

## Содержание

- [Обзор](#обзор)
- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Архитектура](#архитектура)
- [API Reference — pygamejr](#api-reference--pygamejr)
  - [Игровой цикл](#игровой-цикл)
  - [Управление сценами](#управление-сценами)
  - [Спрайты](#спрайты)
  - [Ресурсы](#ресурсы)
  - [TileMap](#tilemap)
- [API Reference — codomir](#api-reference--codomir)
  - [Игрок (player)](#игрок-player)
  - [Карты (maps)](#карты-maps)
- [Примеры](#примеры)
- [Структура проекта](#структура-проекта)

---

## Обзор

`pygamejr` — тонкая обёртка над [pygame-ce](https://pyga.me/), разработанная для обучения программированию с нуля.
Библиотека содержит два устанавливаемых пакета:

| Пакет | Описание |
|-------|----------|
| `pygamejr` | Базовый движок: спрайты, сцены, игровой цикл |
| `codomir` | Квест-слой: тайловое движение персонажа по `.tmx`-картам |

---

## Установка

```bash
# Клонировать репозиторий
git clone https://github.com/benefitkids/pygamejr.git
cd pygamejr

# Установить в режиме редактирования
pip install -e .
```

**Зависимости** (устанавливаются автоматически):
- `pygame-ce` — community-edition версия pygame
- `pytmx` — загрузчик карт Tiled в формате `.tmx`

---

## Быстрый старт

### Минимальный пример

```python
import pygamejr

bee = pygamejr.ImageSprite(pygamejr.resources.image.bee)
pygamejr.wait_quit()
```

### Квест-игра (codomir)

```python
from codomir import player, wait_quit

player.move_forward()
player.turn_right()
player.move_forward()
wait_quit()
```

### Запуск демо-файлов

```bash
python demo/1simple.py
python demo/scene.py
python demo/codomir/loop/map1.py
```

---

## Архитектура

```
pygamejr/
├── pygamejr/          # базовый движок
│   ├── base.py        # инициализация pygame, экран, игровой цикл, переключение сцен
│   ├── scene.py       # Scene — контейнер именованных групп спрайтов
│   ├── tilemap.py     # TileMap — обёртка над pytmx
│   ├── sprite/        # классы спрайтов
│   │   ├── base.py    # BaseSprite
│   │   ├── image.py   # ImageSprite
│   │   ├── text.py    # TextSprite
│   │   ├── circle.py  # CircleSprite
│   │   ├── rect.py    # RectSprite
│   │   └── subtitles.py  # SubtitlesSprite
│   └── resources/     # встроенные изображения и резолвер путей
└── codomir/           # квест-слой
    ├── quest.py       # QuestScene, Player, Direction
    ├── maps/          # константы путей к .tmx-картам
    └── resources/     # ресурсы codomir
```

### Система двух сцен

В любой момент в игре работают два слоя:

- **Глобальная сцена** — всегда рендерится поверх; хранит HUD-элементы, которые живут через смену уровней.
  Спрайты, созданные _до_ первого вызова `set_scene()`, попадают сюда автоматически.
- **Текущая сцена** — активная игровая сцена; меняется через `set_scene()`.
  Спрайты, созданные _после_ `set_scene()`, попадают сюда автоматически.

### Побочные эффекты при импорте

Импорт `pygamejr` вызывает `pygame.init()` и создаёт окно немедленно.
Импорт `codomir` дополнительно загружает карту по умолчанию, строит сцену и создаёт синглтон `player`.

---

## API Reference — pygamejr

### Игровой цикл

#### `every_frame(frame_count=0, draw_sprites_rect=False)`

Генератор, управляющий главным игровым циклом на 60 fps.
На каждом кадре выдаёт `dt` (время в секундах с прошлого кадра).
Автоматически обрабатывает события pygame и рендерит спрайты.

```python
for dt in pygamejr.every_frame():
    sprite.rect.x += 100 * dt   # движение, независимое от fps
```

| Параметр | По умолчанию | Описание |
|----------|--------------|----------|
| `frame_count` | `0` | Остановиться после N кадров (0 = бесконечно) |
| `draw_sprites_rect` | `False` | Рисовать прямоугольники коллизий для отладки |

#### `wait_quit()`

Блокирует выполнение, пока пользователь не закроет окно.

#### `next_frame()`

Рендерит ровно один кадр (используется внутри `codomir` для тайловых анимаций).

#### `is_quit() -> bool`

Возвращает `True`, если получено событие закрытия окна.

---

### Управление сценами

#### `set_scene(scene: Scene)`

Устанавливает активную сцену. Вызывает `scene.init_scene()` и сбрасывает цель автоматической регистрации спрайтов.

#### `get_current_scene() -> Scene | None`

Возвращает текущую (игровую) сцену.

#### `get_global_scene() -> Scene`

Возвращает глобальную (HUD) сцену, создавая её при первом обращении.

---

### `Scene`

Контейнер именованных групп спрайтов.

```python
scene = pygamejr.Scene()
```

| Метод | Описание |
|-------|----------|
| `add(sprite)` | Добавить спрайт в слой `"default"` |
| `remove(sprite)` | Удалить спрайт из слоя `"default"` |
| `add_sprite_list(name, group)` | Зарегистрировать именованную группу `LayeredUpdates` |
| `get_sprite_list(name) -> LayeredUpdates` | Получить именованную группу |
| `update(dt)` | Обновить все группы |
| `draw(draw_rect=False)` | Отрисовать все группы; `draw_rect=True` показывает ректы |
| `init_scene()` | Вызывается при активации сцены (переопределяйте этот метод) |
| `Scene.from_tilemap(tilemap)` | Метод класса — создать сцену из `TileMap` |

---

### Спрайты

Все спрайты автоматически регистрируются в текущей (или глобальной) сцене при создании.
Передайте `scene=` для явного указания сцены.

#### `BaseSprite`

```python
pygamejr.sprite.BaseSprite(sprite_angle=0, is_visible=True, scene=None)
```

| Свойство/Метод | Описание |
|----------------|----------|
| `rect` | `pygame.Rect` — позиция и размер |
| `is_visible` | Показать/скрыть спрайт |
| `move_forward(distance=1.0)` | Двигаться в направлении `sprite_angle` |
| `rotate(angle)` | Повернуть на `angle` градусов |

#### `ImageSprite`

```python
pygamejr.ImageSprite(filename=None, image=None, crop_alpha=True,
                     sprite_angle=0, scene=None)
```

Загружает изображение из файла или `pygame.Surface`.
Автоматически обрезает прозрачные края и создаёт попиксельную маску для коллизий.

```python
bee = pygamejr.ImageSprite(pygamejr.resources.image.bee)
bee.rect.center = (400, 300)
```

| Параметр | Описание |
|----------|----------|
| `filename` | Путь к файлу изображения |
| `image` | `pygame.Surface` для прямого использования |
| `crop_alpha` | Обрезать прозрачную рамку (по умолчанию `True`) |

| Метод | Описание |
|-------|----------|
| `rotate(angle)` | Повернуть изображение и обновить маску коллизий |
| `turn_left(angle=1)` | Повернуть против часовой стрелки |
| `turn_right(angle=1)` | Повернуть по часовой стрелке |

#### `TextSprite`

```python
pygamejr.TextSprite(text='', size=32, color=(255, 255, 255),
                    font_name=None, sprite_angle=0, scene=None)
```

Рендерит текст как спрайт. Изменение свойства `.text` автоматически перерисовывает текст.

```python
label = pygamejr.TextSprite("Счёт: 0", size=24, color=(255, 255, 0))
label.text = "Счёт: 10"   # обновляется автоматически
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

Прокручивающийся текстовый оверлей — поочерёдно показывает строки из списка с интервалом 3 секунды, затем скрывается.

```python
pygamejr.sprite.SubtitlesSprite(
    text_list=["Привет!", "Добро пожаловать в игру."],
    size=28, color=(255, 255, 255)
)
```

---

### Ресурсы

#### `pygamejr.resources.image`

Модуль именованных констант для встроенных изображений.

```python
pygamejr.resources.image.bee
pygamejr.resources.image.coin_gold
pygamejr.resources.image.player_ship1_orange
pygamejr.resources.image.meteor_grey_big1
```

**Категории:**

| Категория | Примеры |
|-----------|---------|
| Существа | `bee`, `fly`, `frog`, `ladybug`, `mouse`, `worm_green` |
| Враги | `slime_blue`, `slime_green`, `saw`, `fish_swim1` |
| Предметы | `coin_gold`, `gem_blue`, `key_gold`, `star_gold` |
| Космический шутер | `player_ship1_orange`, `laser_blue01`, `meteor_grey_big1` |
| UI | `flag_green1`, `ladder_mid`, `lives` |

---

### TileMap

```python
tilemap = pygamejr.TileMap("path/to/map.tmx")
sprites = tilemap.get_layer_sprites("Ground")
```

| Метод | Описание |
|-------|----------|
| `get_layer_sprites(layer_name)` | Возвращает `list[ImageSprite]` для именованного тайлового слоя |
| `tmxdata` | Сырой объект `pytmx` |

---

## API Reference — codomir

### Игрок (player)

Синглтон `player` создаётся автоматически при импорте codomir.

```python
from codomir import player, wait_quit
```

| Метод | Описание |
|-------|----------|
| `player.move_forward()` | Пройти один тайл (64 пкс) в текущем направлении с анимацией |
| `player.turn_left()` | Повернуть на 90° против часовой стрелки |
| `player.turn_right()` | Повернуть на 90° по часовой стрелке |

Игрок автоматически определяет:
- **Стены** — блокируют движение, воспроизводится анимация тряски
- **Победный тайл** — воспроизводится анимация победы и выполнение останавливается

#### `set_map(map_path)` / `init(map_path)`

Загрузить новую `.tmx`-карту и переместить игрока на тайл спавна.

```python
from codomir import set_map, maps

set_map(maps.linear.map2)
```

---

### Карты (maps)

```python
from codomir import maps

maps.linear.map1         # линейная карта 1
maps.linear.map2         # линейная карта 2
# ...
maps.loop.map_loop1      # карта с циклом 1
maps.pirates.linear.map1 # пиратская карта
```

**Коллекции карт:**

| Модуль | Описание |
|--------|----------|
| `maps.linear` | Прямолинейные карты (map1 – map6) |
| `maps.loop` | Карты с циклом (map_loop1 – map_loop6) |
| `maps.nested_loops` | Карты с вложенными циклами |
| `maps.pirates.linear` | Карты в пиратской тематике |

---

## Примеры

### Простая анимация

```python
import pygamejr

bee = pygamejr.ImageSprite(pygamejr.resources.image.bee)
bee.rect.center = (400, 300)

for dt in pygamejr.every_frame():
    bee.move_forward(150 * dt)
```

### Игра с несколькими сценами и HUD

```python
import pygamejr
import pygame

# --- Глобальная сцена (HUD, всегда видна) ---
score_label = pygamejr.TextSprite("Счёт: 0", size=24)
score_label.rect.topleft = (10, 10)

# --- Уровень 1 ---
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
        score_label.text = f"Счёт: {score}"
```

### Квест на кастомной карте

```python
from codomir import player, wait_quit, set_map, maps

set_map(maps.linear.map3)

player.move_forward()
player.move_forward()
player.turn_right()
player.move_forward()

wait_quit()
```

### Тайловый мир из .tmx-файла

```python
import pygamejr

tilemap = pygamejr.TileMap("levels/world.tmx")
scene = pygamejr.Scene.from_tilemap(tilemap)
pygamejr.set_scene(scene)

pygamejr.wait_quit()
```

### Переход между уровнями

```python
import pygamejr
import pygame

# HUD — в глобальной сцене
hud = pygamejr.TextSprite("Уровень 1", size=28)
hud.rect.center = (400, 20)

# Уровень 1
level1 = pygamejr.Scene()
pygamejr.set_scene(level1)
sprite1 = pygamejr.ImageSprite(pygamejr.resources.image.bee)
sprite1.rect.center = (400, 300)

for dt in pygamejr.every_frame():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_n]:
        # Переход на уровень 2
        level2 = pygamejr.Scene()
        pygamejr.set_scene(level2)
        hud.text = "Уровень 2"
        pygamejr.ImageSprite(pygamejr.resources.image.frog).rect.center = (200, 300)
```

---

## Структура проекта

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
├── README.md
└── README_RU.md
```

---

## Настройка окна

Управляйте размером окна через переменные окружения до импорта `pygamejr`:

```bash
PYGAMEJR_WINDOW_WIDTH=1024 PYGAMEJR_WINDOW_HEIGHT=768 python my_game.py
```

---

## Лицензия

MIT © Alexander Mironov
