from codomir import player, wait_quit, set_map, maps

set_map(maps.loop.map4)

for i in range(3):
    player.move_forward()
    player.move_forward()
    player.turn_right()

wait_quit()
