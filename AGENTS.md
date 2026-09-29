# Repository Guidelines

## Project Structure & Module Organization

`src/pygamejr/` contains the core game loop, scenes, sprites, and tile maps. `src/codomir/` builds quests and maps on that library. Keep package images and TMX maps under their existing `resources/` directories; demo-specific assets belong in `demo/assets/` or beside the relevant demo. `demo/` contains runnable examples, and `tests/` contains the `pytest` suite. Packaging and test settings live in `pyproject.toml`.

## Codomir Map Types & Learning Goals

Maps for `codomir` are tile maps created with the Tiled map editor.

`codomir` has three types of maps, each focused on a specific programming concept:

- `linear`: children learn that a program is a sequence of commands. Solutions use only sequential commands, without loops or conditionals.
- `loop`: children practice simple `for i in range(...)` loops.
- `nested_loops`: children practice nested loops.

## Build, Test & Development Commands

On the headless Cloud VM, activate the existing environment and set SDL drivers before importing either package:

```bash
source .venv/bin/activate
export SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy
python -m pip install -e '.[test]'
python -m pytest
```

The editable install picks up local code changes and installs `pytest`; the final command runs all tests. With a real display, run an example using `python demo/1simple.py`. Most demos keep the window open until you close it, so use a bounded driver or timeout for headless smoke checks. There is no server to start.

## Coding Style & Naming Conventions

Follow the existing Python style: four-space indentation, `snake_case` modules and functions, and `CapWords` classes. Keep public examples readable for learners and place new assets beside the code that uses them. No formatter or linter is configured in `pyproject.toml`; avoid introducing formatting-only churn.

## Testing Guidelines

Add focused tests in `tests/test_*.py` using `test_*` functions. Cover both successful behavior and relevant error paths when changing library code. `tests/conftest.py` sets dummy SDL drivers for the main test process; export them in the parent shell too, because `codomir` tests launch subprocesses. Both packages initialize display state during import, so set the drivers first. The project defines no coverage threshold.

## Commit & Pull Request Guidelines

Recent commits use short subjects, often imperative, such as `Add pytest test suite covering pygamejr and codomir (#3)`. Use a concise subject that names the change and include an issue number when applicable. In pull requests, explain the behavior changed, list verification commands and results, and link relevant issues. Include a screenshot or short recording for visible rendering changes.

## Agent Runbook

Read [`.cursor/skills/cloud-agent-starter.md`](.cursor/skills/cloud-agent-starter.md) before working on this repository. It documents import-time side effects and area-specific headless checks. Update it when you discover a reusable testing or environment detail.
