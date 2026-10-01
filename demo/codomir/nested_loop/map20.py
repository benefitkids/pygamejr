# Последний путь к сокровищу
from codomir import player, wait_quit, set_map, maps

set_map(maps.nested_loops.map20)

player.move_forward()
for i in range(2):
    for j in range(2):
        player.move_forward()
    player.turn_left()
    player.move_forward()
    player.turn_right()
player.turn_left()
for i in range(1, 3):
    for j in range(i):
        player.move_forward()
    player.turn_left()
    player.move_forward()
    player.turn_right()
player.move_forward()

wait_quit()
