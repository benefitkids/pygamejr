# Conditions series verification

Verified on 2026-11-09 with Windows, Python 3.11.9, pygame-ce 2.5.8,
SDL 2.32.10 and pytest 9.2.0. The scope is the ten conditions maps and
their accompanying [lesson](conditions.md).

Map 3 was revised on 2026-11-15 to match the nested-loop demo: turn right,
push three times, repeat twice. The hero starts at `(5, 1)` facing right,
travels down to `(5, 4)`, then left to the coin at `(2, 4)`. Initial boxes:
`(5, 2)` and `(4, 4)`; final boxes: `(5, 5)` and `(1, 4)`. The public demo
has four teaching lines, the shortest linear control has eight commands,
and the conditional teacher solution has six checks and two turns (26 lines).
The original series results below describe the earlier snapshot.

## Map 3 verification on 2026-11-15

Windows, Python 3.14.6, pygame-ce 2.5.8, pytest 9.1.1, SDL dummy:

```powershell
New-Item -ItemType Directory -Force .tmp | Out-Null
.venv/Scripts/python.exe -m pytest tests/test_codomir_conditions.py tests/test_codomir_validator.py -k 'map3 or box_at_turn or rejects_noneducational_python or rejects_nested_loop' -p no:cacheprovider --basetemp=.tmp/map3-revised2 --tb=short
```

All 14 selected tests passed. Acceptance covers the main layout and four
variants with real rendering, matches model traces, and confirms the shortest
linear length by BFS. The public nested-loop demo wins after reset, with exact
box positions and one completion callback per run. Introductory conditional
solutions still reject loops; explicit loop controls allow map3's public demo.
Both lesson schemas and all three examples are checked against the manifest.

## Latest maps 1, 2 and 4 verification on 2026-11-15

Map 1 matches two pushes: Spawn `(0, 3)`, box `(1, 3)`, Win `(2, 3)`,
pocket `(3, 3)`. Its conditional reference has two checks (8 lines) and
supports removing the box or putting it on Win.

Map 2 matches one step and two pushes: Spawn `(0, 3)`, box `(2, 3)`,
Win `(3, 3)`, pocket `(4, 3)`. Its conditional reference has three checks
(12 lines) and supports no box, a box next to the start, or a box on Win.

Map 4 now repeats a left turn and six conditional advances twice. Spawn is
`(7, 7)` facing right; the route goes up to `(7, 1)`, then left to Win `(1, 1)`.
Boxes move from `(7, 5)` / `(3, 1)` to `(7, 0)` / `(0, 1)`. First-box variants
are `(7, 6)` and `(7, 2)`. `initial_turn=left` and the complex-route stage allow
the nested loops. Counts are 14 linear commands, 7 conditional lines and
9 lines for the loop control without conditions. Maps 5–6 retain the simple
loop restriction. Map 3 retains its previous geometry and public example.

```powershell
$env:SDL_VIDEODRIVER = 'dummy'
$env:SDL_AUDIODRIVER = 'dummy'
New-Item -ItemType Directory -Force .tmp | Out-Null
.venv/Scripts/python.exe -m pytest -p no:cacheprovider --basetemp=.tmp/latest-full --tb=short
```

**273 tests passed in 129.09 seconds.** The focused changed-map and validator
run passed 41 tests. Public scripts, resets, variants, BFS lengths and rendering
checks pass. Both lessons' maps 1–4 schemas, solutions, counts and variant
outcomes match the manifest. Map1/map2/map4 screenshots below were refreshed.
The older wheel results below remain historical.

## Runtime checks

Each of the ten public scripts runs through `runpy.run_path` in its own
subprocess with SDL dummy video/audio. Only the frame clock, long end animations
and `wait_quit` are disabled; movement, sprite updates and drawing remain active.
Every script wins once, then its teaching body wins again on the same scene
after `reset`, without `set_map` hiding reset failures. All ten linear controls
and the seven for-only controls also win on the real engine.

The manifest acceptance tests check all 33 layouts (10 main layouts and 23
variants). They compare semantic TMX geometry with the manifest, validate the
teaching AST, verify the shortest linear command count with BFS, and match
real-engine action traces against the independent model. Commands and sensor
checks after Win are rejected by the scenario wrapper.

The conditional solutions for maps 1–3 prohibit loops and cover both outcomes across their variants, without
requiring shorter code. Maps 5–6 prohibit nested loops; map 4 and maps 7–10 allow them.
For each main layout of maps 4–10, a loop takes both branches in different
iterations of the same invocation. Traces retain the loop source line,
iteration index, sensor result and chosen action in the pytest temporary
directory as `test_conditions_map_acceptanceN/trace-M.json`.

New regression checks also cover loss and reset on every conditions map,
completion callbacks firing once per run, repeated plays, box sprite uniqueness,
and transitions from conditions map9 to `linear`, `loop` and `nested_loops`
and back. These transitions run twice per family. Old box sprites lose their
groups, the player leaves the old scene, and no callback fires during reset
or map replacement.

## Solution lengths

Counts include physical nonempty teaching lines, including `for`, `if` and
`else`; imports, comments, `set_map` and `wait_quit` are excluded. A linear
solution has no loops or conditions. The for-only controls solve the main
layout; their optimality is not claimed.

| Map | Shortest linear | Conditional | For-only control | Linear minus conditional |
| --- | ---: | ---: | ---: | ---: |
| 1 | 2 | 8 | — | -6 |
| 2 | 3 | 12 | — | -9 |
| 3 | 8 | 26 | 4 | -18 |
| 4 | 14 | 7 | 9 | 7 |
| 5 | 18 | 17 | 13 | 1 |
| 6 | 19 | 17 | 13 | 2 |
| 7 | 19 | 12 | 13 | 7 |
| 8 | 23 | 18 | 16 | 5 |
| 9 | 26 | 24 | 20 | 2 |
| 10 | 26 | 24 | 19 | 2 |

Conditions are intentionally longer on introductory maps 1–3. The saving on
maps 4–10 is relative to linear code, not to every possible program without
`if`. The unchanged conditional program also solves the box variants; the
linear and for-only controls are tied to the main layout.

## Original 2026-11-09 commands and results

Run from the repository root in PowerShell:

```powershell
$env:SDL_VIDEODRIVER = 'dummy'
$env:SDL_AUDIODRIVER = 'dummy'
$env:PYTHONDONTWRITEBYTECODE = '1'
New-Item -ItemType Directory -Force artifacts/conditions | Out-Null
.venv/Scripts/python.exe -m pytest tests/test_codomir_conditions.py -k 'public_demo_replay or switch_to_legacy or push_frames' -p no:cacheprovider --basetemp=artifacts/conditions/focused --tb=short
.venv/Scripts/python.exe -m pytest -p no:cacheprovider --basetemp=artifacts/conditions/full --tb=short
```

The focused run passed **15 tests**. The full suite passed **272 tests in
79.37 seconds**, including all ten map acceptance scenarios and existing
linear/loop/nested-loop regressions.

The lesson was also checked against the manifest and demos: ten schemas,
31 syntactically valid Python blocks, 27 complete teacher programs and 23
variant simulations. All seven lesson iteration tables match the corresponding
real-engine traces from the full run. Python comments in the lesson are English.

### Wheel installation

```powershell
$env:PIP_CERT = $env:SSL_CERT_FILE
.venv/Scripts/python.exe -m pip wheel . --no-deps --wheel-dir artifacts/conditions/wheel
.venv/Scripts/python.exe -m pip --disable-pip-version-check install --no-deps --no-compile --target artifacts/conditions/installed artifacts/conditions/wheel/pygamejr-0.0.27-py3-none-any.whl
foreach ($mapNumber in 1..10) {
    .venv/Scripts/python.exe tests/codomir_packaging_check.py artifacts/conditions/installed $mapNumber
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
```

The wheel built successfully and all **10 installed-package scenarios passed**
in separate processes. The checker asserts that both Python packages and each
public TMX path resolve inside the install target, so the editable checkout
cannot silently supply missing files. Each repository demo then wins using the
installed modules, TMX, external tileset and images; reset restores its boxes.
The demos themselves remain repository examples, outside the runtime wheel.
Use a fresh target directory when repeating the installation check.

Built artifact: `pygamejr-0.0.27-py3-none-any.whl`, SHA-256
`8db1be581764cf7c9f47affd956892304a9a361b42db72793cdcdeea431fc987`.

## Visual evidence

All saved surfaces are 512×512. Pixel comparisons check that the vacated cell
matches the clean background, the destination contains one correctly aligned
box, and reset exactly restores the initial frame. The last animation frame
must match a fresh draw of the resulting scene. Box group membership and counts
also rule out duplicate dynamic sprites.

| Map | Immediately before pushing | After one push | After reset |
| --- | --- | --- | --- |
| 1 | ![Map1 before pushing](images/map1-before-push.png) | ![Map1 after pushing](images/map1-after-push.png) | ![Map1 reset](images/map1-reset.png) |
| 2 | ![Map2 before pushing](images/map2-before-push.png) | ![Map2 after pushing](images/map2-after-push.png) | ![Map2 reset](images/map2-reset.png) |
| 4 | ![Map4 before pushing](images/map4-before-push.png) | ![Map4 after pushing](images/map4-after-push.png) | ![Map4 reset](images/map4-reset.png) |
| 9 | ![Map9 before pushing](images/map9-before-push.png) | ![Map9 after pushing](images/map9-after-push.png) | ![Map9 reset](images/map9-reset.png) |

On map1 the first push covers the coin without winning; the second puts the
hero on Win. On map2, the hero first steps towards the box. Map4's before-push
frame follows a left turn and one upward step. Reset returns each map to its
original start and box layout. Unoccupied finishes are compared with a clean
render without movable sprites.
