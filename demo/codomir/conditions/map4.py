from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map4)

# Repeat twice: turn left, then advance six cells, checking before each step.
# The route leads up and then left. Use push for a box and move_forward otherwise.
# In Tiled, put the first box at (7, 6) or (7, 2); reuse the same code.
# Teaching lines: linear 14, conditional 7, for-only control 9.

for i in range(2):
    player.turn_left()
    for i in range(6):
        if player.is_box_ahead():
            player.push()
        else:
            player.move_forward()

wait_quit()
