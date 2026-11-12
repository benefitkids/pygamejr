from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map6)

# Cross the U-shaped warehouse: six cells right, six down and five left.
# Turn right between passages. Use three simple loops, without nesting.
# Predict each loop's sensor results and explain the change of branch.
# Hint: recheck the adjacent cell in the current direction on every iteration.
# In Tiled, move the first box one or five cells from the start; reuse this code.
# Teacher: after pushing, the hero and box both move; the box is still ahead.
# Teaching lines: linear 19, conditional 17, for-only control 13.
# The for-only control solves the main layout; it is recorded separately.
# The line saving compares with linear code, not every solution without if.

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
