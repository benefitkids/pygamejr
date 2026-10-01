# Узкая и широкая ступень
from codomir import player, wait_quit, set_map, maps

set_map(maps.nested_loops.map7)

for i in range(2):
    player.move_forward()
    player.turn_left()
    player.move_forward()
    player.turn_right()
    for j in range(2):
        player.move_forward()
    player.turn_left()
    player.move_forward()
    player.turn_right()

wait_quit()
