from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map7)

# Warehouse with left turns.
# Reach the coin via two six-cell passages, then a five-cell passage, turning left.
# The outer loop repeats two six-cell passages, including a turn after each.
# Before running, predict when each inner loop changes from stepping to pushing.
# Hint: Ahead follows the hero: right, then up, then left.
# In Tiled, move the first box one or five cells from the start; reuse this code.
# Teacher: recheck after every push; the box remains ahead in the current direction.
# Use the world state to choose an action, rather than the loop counter.
# Teaching lines: linear 19, conditional 12,
# for-only control 13; the control is recorded separately for the main layout.
# The line saving compares with linear code, not every solution without if.

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
