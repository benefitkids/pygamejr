# Conditions: spot a box and choose an action

A lesson on conditions using ten maps, `maps.conditions.map1`–`map10`.
The goal of every map is to guide **the hero to the coin**. Boxes block the path, but you can push them.
The final box positions help check the program; arranging boxes is not a separate game objective.

You already know how to write a sequence of commands and use `for i in range(...)`.
On maps 1–3, first revisit what you have learned and introduce pushing a box.
On map 4, put repeated checks inside a familiar loop: the turn and passage repeat
in nested loops. Maps 5–6 use simple loops, while maps 7–10 follow more complex
routes where nested loops are allowed.

## Pushing a box

One `player.push()` moves the box one cell and moves the hero into the box’s
previous cell. In a straight passage, the box remains directly ahead of the hero.
If you immediately call `player.move_forward()`, the hero will collide with it.

> Try walking through the first map. The hero runs into the box.

```python
player.move_forward()
```

> Try pushing the box.

```python
player.push()
player.push()
```

> It worked!

### Independent exercise

Solve the second and third maps on your own.

The third map can be made shorter with loops. If a learner first solves it with
sequential commands, ask them to rewrite the solution using loops.

Ask the learners to find the large block that appears twice in the program.
Which commands make up that block?

```python
for i in range(2):
    player.turn_right()
    player.push()
    player.push()
    player.push()

wait_quit()
```

This reduces the program’s length by almost half.
There is another, smaller repetition we can remove:

```python
for i in range(2):
    player.turn_right()
    for j in range(3):
        player.push()

wait_quit()
```

## What the hero can see

### Introducing the problem

Now try the fourth map. Start by solving it without loops.

Let the learners write a sequential solution on their own, then discuss how to
shorten it. Repeating passages with loops, as in the first example, introduces
a problem: the hero travels six cells both vertically and horizontally, but
the boxes are at different positions. We do not know when to walk and when
to push.

We already know that Python has conditions. Could we use them here?
Return to the first map: its simple layout lets us introduce a condition
with a short example.

### Is there a box ahead?

The player has a method that checks whether there is a box directly ahead.

`player.is_box_ahead()` returns a `bool` value:

| Value | What is in the adjacent cell ahead of the hero right now |
| --- | --- |
| `True` | A box |
| `False` | No box |

The call only checks the cell: it does not move the hero or push a box.
“Ahead” depends on the direction the hero faces. After `player.turn_right()` or
`player.turn_left()`, the hero faces a new direction.

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

**The hero detects a box with one method and pushes it with a separate method.**
There may be a wall, the edge of the map or another box behind it. A `False`
result does not guarantee a clear path either: there may be a wall ahead.
That is why you must study the route and count the steps.

### What changes after a push

One `player.push()` moves the box one cell and moves the hero into the box’s
previous cell. In a straight passage, the box remains directly ahead of the hero.
If you immediately call `player.move_forward()`, the hero will collide with it.
Check the sensor **again** before choosing the next action.

For example, map 2 can use three checks in sequence. We can then put those
checks inside a loop:

```python
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
```

```python
for i in range(3):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()
```

On map 1, both checks return `True`. The first push puts the box on the coin,
but the game has not been won. After the second push, the hero enters that cell
and wins. Remove the box, and the same code chooses `else` twice. The condition
adapts the program to the world even though the program contains more lines.

On map 2, the first check returns `False` and the next two return `True`:
the first step brings the hero closer to the box, and after pushing, the box
is still ahead. On map 3, turn right before each three-cell passage: first down,
then left. The conditional version checks the next cell at each step:

```python
player.turn_right()
if player.is_box_ahead():
    player.push()
else:
    player.move_forward()
```

This is a fragment from the middle of map 3’s route. You cannot reuse a result
from before the turn instead of checking again: the adjacent cell is now different.

### Errors and trying again

The game ends in defeat if you:

- call `player.push()` when there is no box ahead;
- push a box into a wall, beyond the map or into another box;
- call `player.move_forward()` into a box, a wall or beyond the map.

### Why conditions are useful

On the first maps, the benefit of conditions is not obvious: the code has become
longer. Return to the fourth map and try adding conditions there.

```python
for i in range(2):
    player.turn_left()
    for i in range(6):
        if player.is_box_ahead():
            player.push()
        else:
            player.move_forward()
```

This example shows why conditions help when we do not know in advance where
the boxes will be. The hero needs to check for them and choose an action
from what is currently ahead.

## How to work through the maps

First read the diagram, predict the sensor results and write your program.
After running it, compare your predictions with the hero’s actions. The teacher’s
solutions follow the exercise catalog; open them after trying on your own.

Each diagram below has exactly eight rows of eight cells. `#` is a wall, `.` is floor,
`>` is the hero’s start facing right, `B` is a box, `F` is the coin (the Win cell),
and `*` is a box covering the coin. A box on Win is allowed in a variant; only the hero reaching it wins.
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

**Learning goal:** Choose an action based on whether a box is ahead.

**Task:** Solve the map with two `push()` calls. Then replace them with two sequential `if/else` blocks, without loops.

**Hint:** After pushing, the box remains ahead.

**Check using the conditional solution:** Remove the box, then place it on the coin at `(2, 3)` in a separate copy. Use the unchanged conditional solution.

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

**Learning goal:** Check again after stepping and pushing.

**Task:** Solve the map with `move_forward()`, `push()`, `push()`. Then replace them with three sequential `if/else` blocks, without loops.

**Hint:** First step into the empty cell; check again before each push.

**Check using the conditional solution:** Try no box, a box next to the start at `(1, 3)`, and a box on the coin at `(3, 3)`. Use the unchanged conditional solution.

### Map 3. A new direction after turning

```text
########
#####>##
#####B##
#####.##
#.F.B.##
#####.##
########
########
```

**Learning goal:** Check the adjacent cell again after changing direction.

**Task:** Repeat twice: turn right, then push three times. The route goes down and then left. The public demo uses nested `for` loops. Then replace the pushes with six sequential `if/else` blocks, keeping both right turns; this conditional version has no loops.

**Hint:** The hero starts facing right. After the first turn, “ahead” is down; after the second, it is left.

**Check using the conditional teacher solution:** remove the first box, the second box or both; then, in a separate copy, move the first box to the corner at `(5, 4)` and leave the second in place. Predict the branches before each run.

### Map 4. Turn left

```text
#######.
.F.B....
#######.
#######.
#######.
#######B
#######.
#######>
```

**Learning goal:** Repeat a turn and a six-step passage using nested loops, checking the next cell on every step.

**Task:** Repeat twice: turn left, then advance six cells. Starting at `(7, 7)` facing right, travel up to `(7, 1)`, then left to `(1, 1)`. Use a check inside the inner loop.

**Hint:** Count the hero’s advances: a push also moves the hero one cell.

**Check using the same code:** place the first box at `(7, 6)`, then at `(7, 2)` in a separate copy. Leave the other boxes in place. Predict the branches before each run.

**Review after predicting:** the actual trace of the first inner loop on the main layout. Iterations are numbered from 1; the `range` counter starts at 0.

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
| 3 | 8 | 26 | 4 |
| 4 | 14 | 7 | 9 |
| 5 | 18 | 17 | 13 |
| 6 | 19 | 17 | 13 |
| 7 | 19 | 12 | 13 |
| 8 | 23 | 18 | 16 |
| 9 | 26 | 24 | 20 |
| 10 | 26 | 24 | 19 |

On maps 1–3, conditions are intentionally longer than linear solutions:
the focus is choosing an action and adapting to different layouts. On maps
4–10, conditional solutions are shorter than **linear** solutions. This does
not mean they are shorter than every program without `if`: on map 5, for
example, the `for` control takes 13 lines compared with 17 conditional lines.
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

**Shortest linear (public demo): 2 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map1)

player.push()
player.push()

wait_quit()
```

**Common mistakes:** Walk into the box instead of pushing; stop when the box covers the coin.

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

**Shortest linear (public demo): 3 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map2)

player.move_forward()
player.push()
player.push()

wait_quit()
```

**Common mistakes:** Push immediately from the start where there is no box; walk into the box after pushing.

### Solutions for map 3

**Conditional: 26 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map3)

player.turn_right()

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

player.turn_right()

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

**Shortest linear: 8 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map3)

player.turn_right()
player.push()
player.push()
player.push()
player.turn_right()
player.push()
player.push()
player.push()

wait_quit()
```

**Public demo: 4 lines with nested loops.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map3)

for i in range(2):
    player.turn_right()
    for i in range(3):
        player.push()

wait_quit()
```

**Common mistakes:** Forget the turn or assume that the sensor still checks to the right after turning; skip the second pair of checks.

### Solutions for map 4

**Conditional: 7 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map4)

for i in range(2):
    player.turn_left()
    for i in range(6):
        if player.is_box_ahead():
            player.push()
        else:
            player.move_forward()

wait_quit()
```

**Shortest linear: 14 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map4)

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
player.move_forward()
player.push()
player.push()
player.push()

wait_quit()
```

**`for` control without `if`: 9 lines.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map4)

player.turn_left()
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
