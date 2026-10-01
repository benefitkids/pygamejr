# Растущие причалы
from codomir import player, wait_quit, set_map, maps

set_map(maps.nested_loops.map16)

for i in range(1, 4):
    for j in range(i):
        player.move_forward()
    player.turn_left()
    player.move_forward()
    player.turn_right()

wait_quit()
