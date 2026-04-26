# Cloud Agent Starter Skill

Minimal practical guide for getting a Cloud agent productive in this repo (`pygamejr` + `codomir`). Read this first whenever you start work here. There is no login flow, no service to bring up, and no real "feature flags"; the equivalents are environment variables and SDL drivers, all documented below.

---

## 0. The 30-second mental model

This is a **library + demo scripts** repository. There is no app server, no database, no auth.

- `src/pygamejr/` — core engine (sprites, scenes, game loop) on top of `pygame-ce`.
- `src/codomir/` — quest/map layer built on top of `pygamejr`.
- `demo/` — runnable example scripts; each script runs a **blocking** `pygame` window loop until the window is closed.
- No automated tests exist. "Testing" means: run a demo (or a small repro script) headless, and capture a screenshot or assert on internal state.

**Critical import-time side effects** — know these before you write any test script:

- `import pygamejr` calls `pygame.init()` and creates the window immediately (`src/pygamejr/base.py`).
- `import codomir` *additionally* loads the default `.tmx` map, builds the scene, instantiates the `player` singleton, and renders one frame (`src/codomir/quest.py`).

You cannot defer these by ordering imports differently — set env vars **before** the import.

---

## 1. Environment setup

A `.venv/` is already present in the repo root and has `pygamejr` installed in editable mode along with `pygame-ce` and `pytmx`.

```bash
source .venv/bin/activate
python -c "import pygamejr, codomir; print('ok')"
```

If the venv is missing or stale:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

There is **nothing to log into**. There is no `.env` file and no secrets are required.

### Headless (Cloud agent default)

The Cloud VM has no real display or audio. Always export these before running anything that imports `pygamejr` or `codomir`:

```bash
export SDL_VIDEODRIVER=dummy
export SDL_AUDIODRIVER=dummy
```

With these set, `pygame.display.set_mode(...)` succeeds against an off-screen surface and `pygame.image.save(screen, ...)` still works for screenshots. ALSA warnings on stderr are harmless.

### "Feature flags" / configuration knobs

The only runtime configuration the codebase reads:

| Env var                  | Read in                  | Effect                                  |
|--------------------------|--------------------------|-----------------------------------------|
| `PYGAMEJR_WINDOW_WIDTH`  | `src/pygamejr/base.py`   | Window width (default `800`).           |
| `PYGAMEJR_WINDOW_HEIGHT` | `src/pygamejr/base.py`   | Window height (default `600`).          |
| `SDL_VIDEODRIVER=dummy`  | SDL                      | Required for headless rendering.        |
| `SDL_AUDIODRIVER=dummy`  | SDL                      | Silences audio init in headless VMs.    |
| `SDL_VIDEO_WINDOW_POS`   | set internally by `codomir/quest.py` to position the codomir window | You don't usually touch this. |

`codomir` overwrites `PYGAMEJR_WINDOW_WIDTH`/`_HEIGHT` to `512` in its module-init (8 × 64 px tiles), so do not bother setting those when targeting `codomir`.

There is **no feature-flag system to mock**. If a future change introduces one, document the new env var or stub here.

---

## 2. Running the app(s)

### Running a demo interactively (only useful with a real display)

```bash
python demo/1simple.py
python demo/scene.py
python demo/codomir/loop/map1.py
```

These block until the window closes. On Cloud VMs without a display this will appear to hang — use the headless workflows below instead.

### Running a demo headless for a fixed number of frames

`pygamejr.every_frame(frame_count=N)` exits after `N` frames. Most demos use `wait_quit()` (infinite). To run them headless and bounded, **write a tiny driver** that imports the demo's setup and then drives the loop yourself, or run with a `timeout` and `SDL_*=dummy`:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy timeout 5 python demo/1simple.py
```

`timeout 5` will exit non-zero (124); that is expected for `wait_quit()` demos and is **not a failure**.

For deterministic output, prefer a custom driver script:

```python
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame, pygamejr

bee = pygamejr.ImageSprite(pygamejr.resources.image.bee)
bee.rect.center = (200, 200)
for dt in pygamejr.every_frame(60):
    bee.move_forward(60 * dt)
pygame.image.save(pygamejr.screen, "/tmp/bee.png")
```

---

## 3. Testing workflows by codebase area

There is no `pytest` suite. The patterns below are what a Cloud agent should produce when asked to verify a change.

### 3.1 `src/pygamejr/` — core engine

Typical changes: sprite rendering, scene management, `every_frame` loop, tilemap loader.

**Smoke test** — proves the package still imports and initializes:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
python -c "import pygamejr; print(pygamejr.screen.get_size())"
```

Expected: `(800, 600)`.

**Render-a-frame test** — proves draw pipeline is intact:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python - <<'PY'
import pygame, pygamejr
sp = pygamejr.ImageSprite(pygamejr.resources.image.bee)
sp.rect.center = (100, 100)
for _ in pygamejr.every_frame(5):
    pass
pygame.image.save(pygamejr.screen, "/opt/cursor/artifacts/pygamejr_smoke.png")
PY
```

Attach the resulting PNG as a walkthrough artifact.

**Scene-switching test** — proves `set_scene` + global scene behaviour, useful when touching `base.py` / `scene.py`:

```python
import pygamejr
hud = pygamejr.TextSprite("HUD", size=20)            # global
level = pygamejr.Scene(); pygamejr.set_scene(level)
sp = pygamejr.ImageSprite(pygamejr.resources.image.bee)  # current
assert hud in pygamejr.get_global_scene().get_sprite_list("default")
assert sp in level.get_sprite_list("default")
```

**TileMap test** — when touching `tilemap.py`, load a map shipped with `codomir`:

```python
from codomir.maps.linear import map1
import pygamejr
tm = pygamejr.TileMap(map1)
assert tm.get_layer_sprites("walls"), "walls layer missing"
```

### 3.2 `src/codomir/` — quest/map layer

Typical changes: `Player` movement, win/lose logic, `set_map`, character animation.

The `player` singleton is created on import. Movement methods (`move_forward`, `turn_left`, `turn_right`) **block** while the tile animation runs (60 frames per tile). Always run headless with `SDL_VIDEODRIVER=dummy` so the animation does not require a display.

**Important:** `_animate_win` runs ~10 s of frames after a win and `_animate_game_over` runs a multi-second shake. For fast assertions, monkey-patch them to no-ops before triggering the end state:

```python
from codomir import player
player._animate_win = lambda: None
player._animate_game_over = lambda dx, dy: None
```

**Win path (default map = `maps.linear.map1`):**

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python - <<'PY'
from codomir import player
player._animate_win = lambda: None
player._animate_game_over = lambda dx, dy: None
player.move_forward()
player.move_forward()
assert player.is_finished and player.is_win, (player.is_finished, player.is_win)
print("win OK")
PY
```

Verified on this VM: `finished: True win: True game_over: False` in ~2.5 s.

**Wall / game-over path** (turn into a wall on `map1`):

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python - <<'PY'
from codomir import player
player._animate_win = lambda: None
player._animate_game_over = lambda dx, dy: None
player.turn_left()        # face up — wall on map1
player.move_forward()
assert player.is_finished and player.is_game_over
print("game over OK")
PY
```

Verified: `finished: True win: False game_over: True`.

**Map switching** — when touching `set_map`/`init`:

```python
from codomir import player, set_map, maps
set_map(maps.linear.map3)
assert not player.is_finished
```

**Screenshot of final state** for visual evidence:

```python
import pygame, pygamejr
pygame.image.save(pygamejr.screen, "/opt/cursor/artifacts/codomir_final.png")
```

### 3.3 `demo/` — example scripts

Treat these as *executable documentation*, not tests. Most are infinite loops. When changing a demo:

1. Run the unmodified version of any other demo (e.g. `demo/1simple.py`) headless to confirm engine still runs.
2. Run **the modified demo** headless under `timeout` to confirm it does not crash:

   ```bash
   SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy timeout 3 python demo/<modified>.py; \
   echo "exit=$? (124 == timeout, expected for wait_quit demos)"
   ```

3. If the demo demonstrates new behaviour, write a tiny bounded driver that exercises the same code path for `N` frames and saves a screenshot to `/opt/cursor/artifacts/`.

### 3.4 `pyproject.toml` / packaging

When you change packaging metadata or move files under `src/`:

```bash
source .venv/bin/activate
pip install -e . --force-reinstall --no-deps
python -c "import pygamejr, codomir; print(pygamejr.__file__); print(codomir.__file__)"
```

---

## 4. Common gotchas

- **Window appears at import time.** Set `SDL_VIDEODRIVER=dummy` *before* `import pygamejr`. In an inline `python - <<'PY'` block, set `os.environ["SDL_VIDEODRIVER"]="dummy"` on the first line if you cannot export it in the parent shell.
- **`codomir` overrides window size.** Don't try to set `PYGAMEJR_WINDOW_WIDTH` for a `codomir` test — it will be replaced by `512`.
- **Movement methods block.** `player.move_forward()` runs ~60 frames of animation and is single-threaded. A four-step movement sequence takes a few seconds even headless.
- **Win/game-over animations are slow.** `_animate_win` runs ~10 s of frames; `_animate_game_over` runs a multi-second shake. In tests, monkey-patch `player._animate_win = lambda: None` and `player._animate_game_over = lambda dx, dy: None` before triggering them.
- **`timeout 124` ≠ failure** for any script that ends with `wait_quit()` or contains an unbounded `every_frame()` loop. Check actual output / saved artifact instead of exit code.
- **No automated tests, no linter config.** Don't waste time looking for `pytest`, `ruff`, or CI configuration. If you need to introduce them, ask the user first.
- **ALSA noise on stderr** when audio is real but no card is present. Harmless; `SDL_AUDIODRIVER=dummy` silences it.
- **`is_quit()` is sticky.** Once any module sets the internal flag, the process is dead for further frames; spawn a fresh subprocess per test.

---

## 5. Suggested artifact pattern for Cloud-agent walkthroughs

For UI-affecting changes, save a PNG (or several frames) under `/opt/cursor/artifacts/` and reference it in the walkthrough:

```python
import pygame, pygamejr
# ... set up scene ...
for _ in pygamejr.every_frame(30):
    pass
pygame.image.save(pygamejr.screen, "/opt/cursor/artifacts/<change>_after.png")
```

For multi-step `codomir` tests, save a screenshot after each move:

```python
for i in range(steps):
    player.move_forward()
    pygame.image.save(pygamejr.screen, f"/opt/cursor/artifacts/step_{i}.png")
```

---

## 6. Keeping this skill up to date

This file is the Cloud agent's runbook. **Update it whenever you discover a non-obvious testing trick, environment fix, or workflow shortcut while working in this repo.**

When to edit:

- A new env var, secret, or feature flag is added → document it in §1.
- A new top-level package or area appears under `src/` → add a §3.x sub-section with a smoke test for it.
- A demo or runnable entry point changes its invocation pattern → update §2.
- You burned time on an issue that another agent will hit (e.g. SDL driver quirk, import-time side effect, blocking call) → add a bullet to §4 *Common gotchas*.
- The repo introduces an automated test runner, linter, or CI config → replace the relevant ad-hoc snippet in §3 with the canonical command.

How to edit:

1. Make changes on a feature branch (`cursor/<topic>-<suffix>`), not directly on `main`.
2. Keep entries terse and copy-pasteable. Prefer a one-line shell snippet over prose.
3. If a section grows past ~20 lines of examples, split the deep examples into a new file under `.cursor/skills/` and link to it from here. Keep this file as the **starter** — the first thing an agent reads.
4. Remove obsolete tips immediately; a stale runbook is worse than no runbook.
5. Mention the source of truth (file path) for any documented behaviour, e.g. "see `src/pygamejr/base.py`", so future agents can verify quickly.
