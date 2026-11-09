from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map4)

# Reach the coin by moving six cells right, turning left, then six cells up.
# Put each passage's repeated checks inside a simple for loop.
# Predict the branches in each iteration and explain when the result changes.
# Hint: after turning left, ahead points upward rather than to the right.
# In Tiled, move the first box one or five cells from the start; reuse this code.
# Teacher: check again after every push; the box remains ahead.
# Teaching lines: linear 13, conditional 11, for-only control 8.
# The for-only control solves the main layout; it is recorded separately.
# The line saving compares with linear code, not every solution without if.

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
