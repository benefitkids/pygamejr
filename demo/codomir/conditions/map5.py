from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map5)

# Reach the coin along passages of six, five and five cells, turning right twice.
# Use one simple for loop per passage and check ahead on every iteration.
# Predict when each loop switches from stepping to pushing.
# Hint: passage lengths determine repetitions; boxes determine actions.
# In Tiled, move the first box one or five cells from the start; reuse this code.
# Teacher: after pushing, check again; do not reuse an earlier sensor result.
# Teaching lines: linear 18, conditional 17, for-only control 13.
# The for-only control solves the main layout; it is recorded separately.
# The line saving compares with linear code, not every solution without if.

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
