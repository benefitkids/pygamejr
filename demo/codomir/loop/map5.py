from codomir import player, wait_quit, set_map, maps

set_map(maps.loop.map5)

player.turn_left()

for i in range(5):
    player.move_forward()
    player.turn_left()
    player.move_forward()
    player.turn_right()

wait_quit()
