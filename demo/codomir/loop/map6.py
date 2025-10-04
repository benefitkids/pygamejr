from codomir import player, wait_quit, set_map, maps

set_map(maps.loop.map6)

for i in range(2):
    player.move_forward()
    player.move_forward()
    player.turn_right()
    player.move_forward()
    player.move_forward()
    player.turn_left()

wait_quit()
