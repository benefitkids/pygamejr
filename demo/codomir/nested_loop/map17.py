# Сужающийся пролив
from codomir import player, wait_quit, set_map, maps

set_map(maps.nested_loops.map17)

for i in range(3, 0, -1):
    for j in range(i):
        player.move_forward()
    player.turn_right()
    player.move_forward()
    player.turn_left()

wait_quit()
