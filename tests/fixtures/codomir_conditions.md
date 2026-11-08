# Conditions map acceptance

`codomir_conditions.json` describes the implemented maps, not placeholder maps.
To register the next map, add one entry, its TMX and demo at the conventional
paths, and export `mapN` from `codomir.maps.conditions`. The parametrized
`test_conditions_map_acceptance[mapN]` automatically checks every variant.

Each entry contains:

- `number`, `name`: map identity, numbers 1 through 10, without duplicates.
- `schema`: eight strings of eight cells: `#` wall, `.` floor, `>` Spawn facing
  right, `F` Win, `B` initial box. Coordinates `[x, y]` start at zero.
- `spawn`, `win`, `boxes`: coordinates matching the schema and semantic TMX
  tile types (independent of numeric GIDs).
- `passages`: ordered straight routes, each with `start`, `end`, `length`
  in steps, `turn` (`left`, `right`, or `null` on the last route), and `pocket`
  immediately beyond the end. Pockets are ordinary floor cells.
- `linear_solution`: complete list of Python command lines for the main
  layout; `linear_length` must equal its length and the BFS minimum.
- `conditional_length`: physical nonempty teaching lines in the demo,
  including `for`, `if`, and `else`. Comments, imports, `set_map` and
  `wait_quit` are excluded. One instruction per line is required.
- `final_boxes`: exact expected box coordinates after reaching Win.
- `variants`: records with unique `name`, initial `boxes` and `final_boxes`.
  Geometry and demo source remain identical across variants.
- `learning_stage`, `require_shorter`: maps 1–3 use
  `standalone_conditions` / `false`, 4–6 use
  `conditions_in_simple_loops` / `true`, 7–10 use
  `conditions_in_complex_routes` / `true`.
- For maps 4–10, `loop_solution` and `loop_length`: a complete main-layout
  solution with constant `for range` loops and no `if`. It is validated,
  without requiring it to be longer than the conditional solution.

Target linear/conditional pairs are 2/8, 3/12, 5/17, 13/11,
18/17, 19/17, 19/12, 23/18, 26/24 and 26/24.

Maps 1–3 must contain their specified box variants, including no
boxes and a box on Win. Maps 4–10 move only the first passage's box to
distances 1 and 5 from its start. A box on a turn belongs to the incoming
passage, not the next one.

The validator accepts only direct player commands and explicit
`if player.is_box_ahead(): ... else: ...` decisions. Introductory maps have
no loops; maps 4–6 have no nested loops. Later maps permit nested loops.
Loop bounds are integer constants; data-driven actions, assignments,
functions, `while`, `exec`, ternaries, and step-index conditions are rejected.

Every main layout and variant runs in its own subprocess with SDL dummy.
Only timing and end animations are disabled; movement, sprite updates and
drawing remain active. Traces are saved as `trace-N.json` under the test's
temporary directory. Each row contains `loops` (source line and iteration
index for every active loop), `bool` (sensor result, or null for an
unconditional action), and `action`. Maps 4–10 must exercise both outcomes
in different iterations of the same loop on the **main** layout.

PowerShell verification:

```powershell
$env:SDL_VIDEODRIVER = 'dummy'
$env:SDL_AUDIODRIVER = 'dummy'
New-Item -ItemType Directory -Force artifacts/conditions | Out-Null
.venv/Scripts/python.exe -m pytest tests/test_codomir_conditions.py tests/test_codomir_validator.py -p no:cacheprovider --basetemp=artifacts/conditions/check
```

The parent directory of `--basetemp` must already exist. Acceptance helpers
are in `tests/codomir_validator.py`; importing them does not initialize SDL.
