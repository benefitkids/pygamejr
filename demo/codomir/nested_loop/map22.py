# Извилистый архипелаг
# i — большие участки, j — зигзаги, k — малые ступени.
from codomir import player, wait_quit, set_map, maps

set_map(maps.nested_loops.map22)

for i in range(2):
    for j in range(2):
        for k in range(2):
            player.move_forward()
            player.turn_right()
            player.move_forward()
            player.turn_left()
        player.turn_right()
    player.turn_left()

wait_quit()
