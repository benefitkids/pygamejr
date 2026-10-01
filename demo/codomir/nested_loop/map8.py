# Косой зигзаг
from codomir import player, wait_quit, set_map, maps

set_map(maps.nested_loops.map8)

for i in range(2):
    for j in range(2):
        player.move_forward()
        player.turn_left()
        player.move_forward()
        player.turn_right()
    player.move_forward()

wait_quit()
