from codomir import player, wait_quit, set_map, maps

set_map(maps.loop.map2)

for i in range(4):
    player.move_forward()
    player.turn_right()
    player.move_forward()
    player.turn_left()

wait_quit()
