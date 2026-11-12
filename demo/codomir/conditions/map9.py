from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map9)

# The last pocket.
# Reach the inner coin: six, six, five, three and two cells, turning right.
# The outer loop repeats two six-cell passages, including a turn after each.
# Before running, predict when each inner loop changes from stepping to pushing.
# Hint: A box reaching the coin is not a win; the hero must enter that cell.
# In Tiled, move the first box one or five cells from the start; reuse this code.
# Teacher: recheck after every push; the box remains ahead in the current direction.
# Use the world state to choose an action, rather than the loop counter.
# Teaching lines: linear 26, conditional 24,
# for-only control 20; the control is recorded separately for the main layout.
# The line saving compares with linear code, not every solution without if.

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
