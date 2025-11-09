from codomir import player, wait_quit, set_map, maps

set_map(maps.nested_loops.map2)

for i in range(2):
    for j in range(4):
        player.move_forward()
    player.turn_right()
    player.move_forward()
    player.move_forward()
    player.turn_right()

    for j in range(4):
        player.move_forward()
    player.turn_left()
    player.move_forward()
    player.move_forward()
    player.turn_left()

wait_quit()
