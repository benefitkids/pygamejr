# Conditions: spot a box and choose an action

A lesson on conditions using ten maps, `maps.conditions.map1`–`map10`.
The goal of every map is to guide **the hero to the coin**. Boxes block the path, but you can push them.
The final box positions help check the program; arranging boxes is not a separate game objective.

You already know how to write a sequence of commands and use `for i in range(...)`.
On maps 1–3, set loops aside for a moment and focus on choosing an action.
On map 4, put repeated checks inside a familiar loop. Maps 4–6 use simple loops;
maps 7–10 follow more complex routes where nested loops are allowed.

## What the sensor tells you

`player.is_box_ahead()` returns a `bool` value:

| Value | What is in the adjacent cell ahead of the hero right now |
| --- | --- |
| `True` | A box |
| `False` | No box |

The call only checks the cell: it does not move the hero or push a box.
“Ahead” depends on the direction the hero faces. After `player.turn_right()` or
`player.turn_left()`, the sensor checks the new direction.

An `if` statement chooses an action based on the check. Exactly one branch runs:

```python
if player.is_box_ahead():
    player.push()
else:
    player.move_forward()
```

A colon starts each branch, and four spaces of indentation mark its commands.
When the result is `True`, `push()` runs; when it is `False`, `move_forward()` runs.
This block works for the passages in these maps: with the correct number of steps,
the hero encounters either a free cell or a box with room to move.

**The sensor detects a box; it does not check whether pushing is possible.**
There may be a wall, the edge of the map or another box behind it. A `False`
result does not guarantee a clear path either: there may be a wall ahead.
That is why you must study the route and count the steps.

## What changes after a push

One `player.push()` moves the box one cell and moves the hero into the box’s
previous cell. In a straight passage, the box remains directly ahead of the hero.
If you immediately call `player.move_forward()`, the hero will collide with it.
Check the sensor **again** before choosing the next action.

For example, map 1 uses two checks in sequence, without loops:

```python
if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()
```

On the main layout, both checks return `True`. After the first push, the box
occupies the coin’s cell, but the game has not been won. After the second push,
the hero enters that cell and wins. Remove the box, and the same code chooses
`else` twice. The condition adapts the program to the world even though the
program contains more lines.

On map 2, the first check returns `False` and the next two return `True`:
the first step brings the hero closer to the box, and after pushing, the box
is still ahead. On map 3, two checks are followed by a turn and two fresh checks:

```python
player.turn_right()
if player.is_box_ahead():
    player.push()
else:
    player.move_forward()
```

This is a fragment from the middle of map 3’s route. You cannot reuse a result
from before the turn instead of checking again: the adjacent cell is now different.

## Errors and trying again

The game ends in defeat (`player.is_game_over`) if you:

- call `player.push()` when there is no box ahead;
- push a box into a wall, beyond the map or into another box;
- call `player.move_forward()` into a box, a wall or beyond the map.

After a failed push, both the hero and the box stay in their cells.
To try again, reset the map before running your corrected solution:

```python
player.reset()
```

Reset restores the selected map’s initial boxes, returns the hero to the start
facing right, and clears the win or defeat state. Use `set_map(...)` to select another map.

## How to work through the maps

First read the diagram, predict the sensor results and write your program.
After running it, compare your predictions with the hero’s actions. The teacher’s
solutions follow the exercise catalog; open them after trying on your own.

Each diagram below has exactly eight rows of eight cells. `#` is a wall, `.` is floor,
`>` is the hero’s start facing right, `B` is a box, and `F` is the coin (the Win cell).
Coordinates `(x, y)` start at zero in the top-left corner; `x` increases to the right
and `y` increases downward. A free cell beyond the end of a passage is a pocket
for its box. The hero stops earlier, at a corner or the coin. A pocket is ordinary
floor, not a special target.

To check whether your solution adapts, open a **copy** of the TMX file in Tiled
and change only the boxes in the `boxes` layer. Keep the floor, walls, start and
coin unchanged. Load the copy with `set_map("path/to/variant.tmx")` and leave
the solving part of your program unchanged. Each exercise lists its variants below.
Choose the action using the sensor, rather than the step number `i`: moving a
box changes the step on which the hero encounters it.

## Exercise catalog

### Map 1. First choice: push or step forward

```text
########
########
########
>BF.####
########
########
########
########
```

**Learning goal:** Learn to choose between two actions using a `bool` value.

**Task:** Guide the hero to the coin in two advances. Write two `if/else` blocks in sequence, without `for` or `while`.

**Hint:** After a successful push, the box is still ahead of the hero.

**Check using the same code:** remove the box; then, in a separate copy, place it on the coin at `(2, 3)`. Predict the branches before each run.

### Map 2. Check again after pushing

```text
########
########
########
>.BF.###
########
########
########
########
```

**Learning goal:** Notice how the sensor result changes after a step, and check again after a push.

**Task:** Guide the hero to the coin in three advances. Write three `if/else` blocks in sequence, without `for` or `while`.

**Hint:** First count the free cells between the start and the box.

**Check using the same code:** remove the box; then, in separate copies, place it next to the start at `(1, 3)` or on the coin at `(3, 3)`. Predict the branches before each run.

### Map 3. A new direction after turning

```text
########
#>B..###
###B####
###F####
###.####
########
########
########
```

**Learning goal:** Check the adjacent cell again after changing direction.

**Task:** Follow two short passages with a right turn between them. Use four sequential `if/else` blocks and a turn, without `for` or `while`.

**Hint:** After the turn, “ahead” means the adjacent cell below the hero.

**Check using the same code:** remove the first box, the second box or both; then, in a separate copy, move the first box to the corner at `(3, 1)` and leave the second in place. Predict the branches before each run.

### Map 4. Turn left

```text
######.#
######F#
######.#
######B#
######.#
######.#
######.#
>.B.....
```

**Learning goal:** Put a repeated `if/else` block inside a familiar simple `for` loop.

**Task:** Move six cells right, turn left and move six cells up. Use a simple loop with a check inside it for each passage.

**Hint:** Count the hero’s advances: a push also moves the hero one cell.

**Check using the same code:** place the first box at `(1, 7)`, then at `(5, 7)` in a separate copy. Leave the other boxes in place. Predict the branches before each run.

**Review after predicting:** the actual trace of the first simple loop on the main layout. Iterations are numbered from 1; the `range` counter starts at 0.

| Iteration | `is_box_ahead()` | Chosen action |
| --- | --- | --- |
| 1 | `False` | `player.move_forward()` |
| 2 | `True` | `player.push()` |
| 3 | `True` | `player.push()` |
| 4 | `True` | `player.push()` |
| 5 | `True` | `player.push()` |
| 6 | `True` | `player.push()` |

Both branches occur within the same loop: the hero first walks through free cells, then pushes. The sensor is checked again on every iteration.

### Map 5. Three passages

```text
>..B....
######.#
######B#
######.#
######.#
.FB....#
######.#
########
```

**Learning goal:** Split the route into three passages and check the sensor inside each loop.

**Task:** Follow passages of 6, 5 and 5 cells with right turns. Use simple loops, checking the cell on every iteration.

**Hint:** At a corner, one passage ends and the next begins.

**Check using the same code:** place the first box at `(1, 0)`, then at `(5, 0)` in a separate copy. Leave the other boxes in place. Predict the branches before each run.

**Review after predicting:** the actual trace of the first simple loop on the main layout. Iterations are numbered from 1; the `range` counter starts at 0.

| Iteration | `is_box_ahead()` | Chosen action |
| --- | --- | --- |
| 1 | `False` | `player.move_forward()` |
| 2 | `False` | `player.move_forward()` |
| 3 | `True` | `player.push()` |
| 4 | `True` | `player.push()` |
| 5 | `True` | `player.push()` |
| 6 | `True` | `player.push()` |

Both branches occur within the same loop: the hero first walks through free cells, then pushes. The sensor is checked again on every iteration.

### Map 6. U-shaped warehouse

```text
>.B.....
######.#
######.#
######.#
######B#
######.#
.F.B...#
######.#
```

**Learning goal:** Choose the repetition count separately for each straight passage.

**Task:** Follow passages of 6, 6 and 5 cells with right turns. Use simple loops without nesting.

**Hint:** The last passage is shorter than the first two.

**Check using the same code:** place the first box at `(1, 0)`, then at `(5, 0)` in a separate copy. Leave the other boxes in place. Predict the branches before each run.

**Review after predicting:** the actual trace of the first simple loop on the main layout. Iterations are numbered from 1; the `range` counter starts at 0.

| Iteration | `is_box_ahead()` | Chosen action |
| --- | --- | --- |
| 1 | `False` | `player.move_forward()` |
| 2 | `True` | `player.push()` |
| 3 | `True` | `player.push()` |
| 4 | `True` | `player.push()` |
| 5 | `True` | `player.push()` |
| 6 | `True` | `player.push()` |

Both branches occur within the same loop: the hero first walks through free cells, then pushes. The sensor is checked again on every iteration.

### Map 7. Warehouse with left turns

```text
######.#
.F..B..#
######.#
######.#
######B#
######.#
######.#
>...B...
```

**Learning goal:** Use a nested loop to repeat passages of the same length together with their turns.

**Task:** Follow passages of 6, 6 and 5 cells with left turns. Combine the two equal passages using an outer loop.

**Hint:** The turn at the end repeats together with the long passage.

**Check using the same code:** place the first box at `(1, 7)`, then at `(5, 7)` in a separate copy. Leave the other boxes in place. Predict the branches before each run.

**Review after predicting:** the actual trace of the first invocation of the inner loop (outer iteration `i = 0`) on the main layout. Iterations are numbered from 1; the `range` counter starts at 0.

| Iteration | `is_box_ahead()` | Chosen action |
| --- | --- | --- |
| 1 | `False` | `player.move_forward()` |
| 2 | `False` | `player.move_forward()` |
| 3 | `False` | `player.move_forward()` |
| 4 | `True` | `player.push()` |
| 5 | `True` | `player.push()` |
| 6 | `True` | `player.push()` |

Both branches occur within the same loop: the hero first walks through free cells, then pushes. The sensor is checked again on every iteration.

### Map 8. Into the spiral

```text
>..B....
######.#
#.####B#
#F####.#
#.####.#
#B####.#
..B....#
######.#
```

**Learning goal:** Combine repeated passages with shorter sections of a spiral.

**Task:** Follow the spiral: 6, 6, 5 and 3 cells, turning right. You can combine the repeated pair of passages using an outer loop.

**Hint:** The inner passage has its own length; do not enter the pocket beyond the coin.

**Check using the same code:** place the first box at `(1, 0)`, then at `(5, 0)` in a separate copy. Leave the other boxes in place. Predict the branches before each run.

**Review after predicting:** the actual trace of the first invocation of the inner loop (outer iteration `i = 0`) on the main layout. Iterations are numbered from 1; the `range` counter starts at 0.

| Iteration | `is_box_ahead()` | Chosen action |
| --- | --- | --- |
| 1 | `False` | `player.move_forward()` |
| 2 | `False` | `player.move_forward()` |
| 3 | `True` | `player.push()` |
| 4 | `True` | `player.push()` |
| 5 | `True` | `player.push()` |
| 6 | `True` | `player.push()` |

Both branches occur within the same loop: the hero first walks through free cells, then pushes. The sensor is checked again on every iteration.

### Map 9. The last pocket

```text
>.B.....
######.#
#.####.#
#.BF.#.#
#B####B#
#.####.#
...B...#
######.#
```

**Learning goal:** Guide the hero to the inner coin while keeping the same action-selection rule.

**Task:** Follow the spiral: 6, 6, 5, 3 and 2 cells, turning right. Stop when the hero reaches the coin.

**Hint:** A box on the coin does not mean you have won yet.

**Check using the same code:** place the first box at `(1, 0)`, then at `(5, 0)` in a separate copy. Leave the other boxes in place. Predict the branches before each run.

**Review after predicting:** the actual trace of the first invocation of the inner loop (outer iteration `i = 0`) on the main layout. Iterations are numbered from 1; the `range` counter starts at 0.

| Iteration | `is_box_ahead()` | Chosen action |
| --- | --- | --- |
| 1 | `False` | `player.move_forward()` |
| 2 | `True` | `player.push()` |
| 3 | `True` | `player.push()` |
| 4 | `True` | `player.push()` |
| 5 | `True` | `player.push()` |
| 6 | `True` | `player.push()` |

Both branches occur within the same loop: the hero first walks through free cells, then pushes. The sensor is checked again on every iteration.

### Map 10. Mirrored spiral

```text
######.#
...B...#
#B####.#
#.####.#
#.BF.#.#
#.####B#
######.#
>...B...
```

**Learning goal:** Apply the familiar algorithm to a mirrored route with left turns.

**Task:** Follow the mirrored spiral: 6, 6, 5, 3 and 2 cells, turning left. Keep the sensor check inside the loops.

**Hint:** Mirroring changes the turns, but the sensor check still means the same thing.

**Check using the same code:** place the first box at `(1, 7)`, then at `(5, 7)` in a separate copy. Leave the other boxes in place. Predict the branches before each run.

**Review after predicting:** the actual trace of the first invocation of the inner loop (outer iteration `i = 0`) on the main layout. Iterations are numbered from 1; the `range` counter starts at 0.

| Iteration | `is_box_ahead()` | Chosen action |
| --- | --- | --- |
| 1 | `False` | `player.move_forward()` |
| 2 | `False` | `player.move_forward()` |
| 3 | `False` | `player.move_forward()` |
| 4 | `True` | `player.push()` |
| 5 | `True` | `player.push()` |
| 6 | `True` | `player.push()` |

Both branches occur within the same loop: the hero first walks through free cells, then pushes. The sensor is checked again on every iteration.

## For teachers: solutions and line counts

The complete programs below solve the main layout. The conditional programs
match the solving part of `demo/codomir/conditions/mapN.py` and also solve the
listed variants without code changes. Linear solutions are tied to the main
layout: moving a box may make their command sequence incorrect.

Count nonempty teaching lines: a command, a `for` header, an `if` header and
an `else` line each count as one line. Imports, comments, `set_map(...)` and
`wait_quit()` are excluded. Each call is written on its own line.
This measures the written program’s length, not the number of movements executed.

The shortest linear program uses only commands, without conditions or loops;
its length is checked by finding the shortest path through the state model.
The `for` control without `if` also solves the main layout. We do not claim
that it is the shortest possible program using loops.

| Map | Shortest linear | Conditional | `for` control without `if` |
| --- | --- | --- | --- |
| 1 | 2 | 8 | — |
| 2 | 3 | 12 | — |
| 3 | 5 | 17 | — |
| 4 | 13 | 11 | 8 |
| 5 | 18 | 17 | 13 |
| 6 | 19 | 17 | 13 |
| 7 | 19 | 12 | 13 |
| 8 | 23 | 18 | 16 |
| 9 | 26 | 24 | 20 |
| 10 | 26 | 24 | 19 |

On maps 1–3, conditions are intentionally longer than linear solutions:
the focus is choosing an action and adapting to different layouts. On maps
4–10, conditional solutions are shorter than **linear** solutions. This does
not mean they are shorter than every program without `if`: on map 4, for
example, the `for` control takes 8 lines compared with 11 conditional lines.
Conditions choose an action from the box’s actual position; a loop repeats
that check.

### Solutions for map 1

**Conditional: 8 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map1)

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

wait_quit()
```

**Shortest linear: 2 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map1)

player.push()
player.push()

wait_quit()
```

**Common mistakes:** Push once and assume that a box on the coin means victory; move forward without checking after a push.

### Solutions for map 2

**Conditional: 12 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map2)

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

wait_quit()
```

**Shortest linear: 3 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map2)

player.move_forward()
player.push()
player.push()

wait_quit()
```

**Common mistakes:** Reuse the first `False` result instead of checking again; think that the box disappears after the first push.

### Solutions for map 3

**Conditional: 17 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map3)

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

player.turn_right()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

wait_quit()
```

**Shortest linear: 5 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map3)

player.push()
player.push()
player.turn_right()
player.push()
player.push()

wait_quit()
```

**Common mistakes:** Forget the turn or assume that the sensor still checks to the right after turning; skip the second pair of checks.

### Solutions for map 4

**Conditional: 11 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map4)

for i in range(6):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

player.turn_left()

for i in range(6):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

wait_quit()
```

**Shortest linear: 13 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map4)

player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.push()
player.turn_left()
player.move_forward()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()

wait_quit()
```

**`for` control without `if`: 8 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map4)

player.move_forward()
for i in range(5):
    player.push()
player.turn_left()
for i in range(3):
    player.move_forward()
for i in range(3):
    player.push()

wait_quit()
```

**Common mistakes:** Check only before starting the loop; reuse the result from the first iteration.

### Solutions for map 5

**Conditional: 17 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map5)

for i in range(6):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

player.turn_right()

for i in range(5):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

player.turn_right()

for i in range(5):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

wait_quit()
```

**Shortest linear: 18 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map5)

player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.move_forward()
player.move_forward()
player.push()
player.push()

wait_quit()
```

**`for` control without `if`: 13 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map5)

for i in range(2):
    player.move_forward()
for i in range(4):
    player.push()
player.turn_right()
player.move_forward()
for i in range(4):
    player.push()
player.turn_right()
for i in range(3):
    player.move_forward()
for i in range(2):
    player.push()

wait_quit()
```

**Common mistakes:** Give all three loops the same length; forget the second turn.

### Solutions for map 6

**Conditional: 17 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map6)

for i in range(6):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

player.turn_right()

for i in range(6):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

player.turn_right()

for i in range(5):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

wait_quit()
```

**Shortest linear: 19 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map6)

player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()

wait_quit()
```

**`for` control without `if`: 13 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map6)

player.move_forward()
for i in range(5):
    player.push()
player.turn_right()
for i in range(3):
    player.move_forward()
for i in range(3):
    player.push()
player.turn_right()
for i in range(2):
    player.move_forward()
for i in range(3):
    player.push()

wait_quit()
```

**Common mistakes:** Reuse the first passages’ length on the last passage and go beyond the coin.

### Solutions for map 7

**Conditional: 12 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map7)

for i in range(2):
    for j in range(6):
        if player.is_box_ahead():
            player.push()
        else:
            player.move_forward()
    player.turn_left()
for i in range(5):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

wait_quit()
```

**Shortest linear: 19 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map7)

player.move_forward()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.turn_left()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.turn_left()
player.move_forward()
player.push()
player.push()
player.push()
player.push()

wait_quit()
```

**`for` control without `if`: 13 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map7)

for i in range(3):
    player.move_forward()
for i in range(3):
    player.push()
player.turn_left()
for i in range(2):
    player.move_forward()
for i in range(4):
    player.push()
player.turn_left()
player.move_forward()
for i in range(4):
    player.push()

wait_quit()
```

**Common mistakes:** Put the turn after the outer loop, so it runs only once.

### Solutions for map 8

**Conditional: 18 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map8)

for i in range(2):
    for j in range(6):
        if player.is_box_ahead():
            player.push()
        else:
            player.move_forward()
    player.turn_right()
for i in range(5):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()
player.turn_right()
for i in range(3):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

wait_quit()
```

**Shortest linear: 23 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map8)

player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.turn_right()
player.push()
player.push()
player.push()

wait_quit()
```

**`for` control without `if`: 16 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map8)

for i in range(2):
    player.move_forward()
for i in range(4):
    player.push()
player.turn_right()
player.move_forward()
for i in range(5):
    player.push()
player.turn_right()
for i in range(3):
    player.move_forward()
for i in range(2):
    player.push()
player.turn_right()
for i in range(3):
    player.push()

wait_quit()
```

**Common mistakes:** Use six repetitions for the short inner passages; miss the turn after five steps.

### Solutions for map 9

**Conditional: 24 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map9)

for i in range(2):
    for j in range(6):
        if player.is_box_ahead():
            player.push()
        else:
            player.move_forward()
    player.turn_right()
for i in range(5):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()
player.turn_right()
for i in range(3):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()
player.turn_right()
for i in range(2):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

wait_quit()
```

**Shortest linear: 26 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map9)

player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.push()
player.push()
player.turn_right()
player.push()
player.push()

wait_quit()
```

**`for` control without `if`: 20 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map9)

player.move_forward()
for i in range(5):
    player.push()
player.turn_right()
for i in range(3):
    player.move_forward()
for i in range(3):
    player.push()
player.turn_right()
for i in range(2):
    player.move_forward()
for i in range(3):
    player.push()
player.turn_right()
player.move_forward()
for i in range(2):
    player.push()
player.turn_right()
for i in range(2):
    player.push()

wait_quit()
```

**Common mistakes:** Stop when the box reaches the coin, or take an extra step after winning.

### Solutions for map 10

**Conditional: 24 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map10)

for i in range(2):
    for j in range(6):
        if player.is_box_ahead():
            player.push()
        else:
            player.move_forward()
    player.turn_left()
for i in range(5):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()
player.turn_left()
for i in range(3):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()
player.turn_left()
for i in range(2):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

wait_quit()
```

**Shortest linear: 26 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map10)

player.move_forward()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.turn_left()
player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.push()
player.turn_left()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.turn_left()
player.push()
player.push()
player.push()
player.turn_left()
player.push()
player.push()

wait_quit()
```

**`for` control without `if`: 19 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map10)

for i in range(3):
    player.move_forward()
for i in range(3):
    player.push()
player.turn_left()
player.move_forward()
for i in range(5):
    player.push()
player.turn_left()
for i in range(2):
    player.move_forward()
for i in range(3):
    player.push()
player.turn_left()
for i in range(3):
    player.push()
player.turn_left()
for i in range(2):
    player.push()

wait_quit()
```

**Common mistakes:** Copy map 9’s right turns; change the action-selection rule instead of the route’s turns.

## Running and checking

From the repository root, with dependencies installed, run a demo, for example in PowerShell:

```powershell
.venv/Scripts/python.exe demo/codomir/conditions/map1.py
.venv/Scripts/python.exe demo/codomir/conditions/map4.py
```

Replace the number with any value from 1 to 10. The window stays open in
`wait_quit()`; close it before the next run. To watch the game, use a normal video driver.

Automated checks without a display (set the variables before importing the packages):

```powershell
$env:SDL_VIDEODRIVER = 'dummy'
$env:SDL_AUDIODRIVER = 'dummy'
New-Item -ItemType Directory -Force artifacts/conditions | Out-Null
.venv/Scripts/python.exe -m pytest tests/test_codomir_conditions.py tests/test_codomir_validator.py -p no:cacheprovider --basetemp=artifacts/conditions/lesson-check
```

`--basetemp` is a separate temporary directory for pytest; do not point it at files you need to keep.
After checking, remove the dummy-driver settings in the same PowerShell session to run visible demos:

```powershell
Remove-Item Env:SDL_VIDEODRIVER
Remove-Item Env:SDL_AUDIODRIVER
```

On Linux with an existing `.venv`:

```bash
source .venv/bin/activate
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m pytest tests/test_codomir_conditions.py tests/test_codomir_validator.py
```

Diagrams, variants and line counts are stored in
[`tests/fixtures/codomir_conditions.json`](../../tests/fixtures/codomir_conditions.json).
The counting rules are explained in the [manifest documentation](../../tests/fixtures/codomir_conditions.md).
Runnable examples are in [`demo/codomir/conditions/`](../../demo/codomir/conditions/).
See the [verification report](conditions-verification.md) for the series checks and results.
