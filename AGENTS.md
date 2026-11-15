# Repository Guidelines

## Project Tasks

Tasks for pygamejr are tracked in Linear: https://linear.app/codomir/project/pygamejr-08f0929fa267/overview. Use this Linear project when working on tasks for this repository.

Store all development plans, task lists, implementation checklists, and task status in Linear, not in Git. Do not create or stage repository planning files such as `docs/*-plan.md`, `docs/tasks.md`, or `docs/superpowers/` plans. If a skill suggests saving a development plan in the repository, use a Linear issue or project document instead. Runnable examples, lessons, reference documentation, and verification reports remain in the repository; link to Linear for planning and task tracking.

## Project Structure & Module Organization

`src/pygamejr/` contains the core game loop, scenes, sprites, and tile maps. `src/codomir/` builds quests and maps on that library. Keep package images and TMX maps under their existing `resources/` directories; demo-specific assets belong in `demo/assets/` or beside the relevant demo. `demo/` contains runnable examples, and `tests/` contains the `pytest` suite. Packaging and test settings live in `pyproject.toml`.

Both packages ship in one distribution, built with `hatchling`; runtime dependencies are `pygame-ce` and `pytmx`.

## Architecture & Runtime Behavior

- Importing `pygamejr` initializes pygame and creates the display in `src/pygamejr/base.py`. Set `PYGAMEJR_WINDOW_WIDTH` and `PYGAMEJR_WINDOW_HEIGHT` before import to change its default window size.
- `every_frame()` drives the update/render loop; `next_frame()` renders a single frame. `wait_quit()` blocks until the window closes, so bound or replace it for automated demo checks.
- The current scene is rendered below the global scene. `BaseSprite` registers with its explicit `scene`, otherwise the current scene, otherwise the global scene. Sprites created before `set_scene()` therefore remain visible across scene changes, which is useful for HUD elements.
- `Scene` stores named sprite groups; the default group is `default`. Sprite classes include `ImageSprite`, `CircleSprite`, `RectSprite`, `TextSprite`, and `SubtitlesSprite`, all based on `BaseSprite`.
- `TileMap` wraps PyTMX map loading and exposes layer sprites through `get_layer_sprites()`. Use the package resource resolvers in `resources/resolve_path.py` for bundled assets instead of paths relative to the working directory.
- Importing `codomir` additionally loads the default map, creates the `QuestScene` and `player` singleton, and renders a frame. It sets the display size to 512×512; import `codomir` before `pygamejr` when checking that size in a fresh process.
- The quest API exposes `player`, `set_map()`, `init()` (which delegates to `set_map()`), and `wait_quit()`. Movement uses 64-pixel tiles and blocks while tile animations run; turns update and render the direction immediately. `player.reset()` restores the selected map's start, direction, boxes, and completion state.
- Map paths are available through `maps.linear`, `maps.loop`, `maps.nested_loops`, `maps.conditions`, and `maps.pirates.linear`. On conditions maps, `player.is_box_ahead()` only checks the adjacent cell; `player.push()` moves both the box and hero. Victory requires the hero to reach Win, even if a box already occupies that cell.

## Codomir Map Types & Learning Goals

Maps for `codomir` are tile maps created with the Tiled map editor.

`codomir` has four main map types, each focused on a specific programming concept:

- `linear`: children learn that a program is a sequence of commands. Solutions use only sequential commands, without loops or conditionals.
- `loop`: children practice simple `for i in range(...)` loops.
- `nested_loops`: children practice nested loops.
- `conditions`: children choose between stepping and pushing with `player.is_box_ahead()`; the introductory demos also revisit sequential commands and nested loops.

## Build, Test & Development Commands

On the headless Cloud VM, activate the existing environment and set SDL drivers before importing either package:

```bash
source .venv/bin/activate
export SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy
python -m pip install -e '.[test]'
python -m pytest
```

The editable install picks up local code changes and installs `pytest`; the final command runs all tests. With a real display, run an example using `python demo/1simple.py`. Most demos keep the window open until you close it, so use a bounded driver or timeout for headless smoke checks. There is no server to start.

On Windows/PowerShell, use the existing virtual environment:

```powershell
$env:SDL_VIDEODRIVER = 'dummy'
$env:SDL_AUDIODRIVER = 'dummy'
.venv/Scripts/python.exe -m pytest
```

## Coding Style & Naming Conventions

Follow the existing Python style: four-space indentation, `snake_case` modules and functions, and `CapWords` classes. Keep public examples readable for learners and place new assets beside the code that uses them. No formatter or linter is configured in `pyproject.toml`; avoid introducing formatting-only churn.

## Testing Guidelines

Add focused tests in `tests/test_*.py` using `test_*` functions. Cover both successful behavior and relevant error paths when changing library code. `tests/conftest.py` sets dummy SDL drivers for the main test process; export them in the parent shell too, because `codomir` tests launch subprocesses. Both packages initialize display state during import, so set the drivers first. The project defines no coverage threshold.

## Commit & Pull Request Guidelines

Recent commits use short subjects, often imperative, such as `Add pytest test suite covering pygamejr and codomir (#3)`. Use a concise subject that names the change and include an issue number when applicable. In pull requests, explain the behavior changed, list verification commands and results, and link relevant issues. Include a screenshot or short recording for visible rendering changes.

## Agent Runbook

Read [`.cursor/skills/cloud-agent-starter.md`](.cursor/skills/cloud-agent-starter.md) before working on this repository. It documents import-time side effects and area-specific headless checks. Update it when you discover a reusable testing or environment detail.
