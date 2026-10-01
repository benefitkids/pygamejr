# Между островами
from codomir import player, wait_quit, set_map, maps

set_map(maps.nested_loops.map11)

for i in range(2):
    for j in range(3):
        player.move_forward()
    player.turn_right()
    player.move_forward()
    player.move_forward()
    player.turn_right()
    player.move_forward()
    player.move_forward()
    player.turn_left()

wait_quit()
