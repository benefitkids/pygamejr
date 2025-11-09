from codomir import player, wait_quit, set_map, maps

set_map(maps.nested_loops.map1)

player.turn_right()
player.turn_right()

for i in range(1, 6):
    for j in range(i):
        player.move_forward()
    player.turn_right()

wait_quit()