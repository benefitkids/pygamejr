from codomir import player, wait_quit, set_map, maps

set_map(maps.loop.map6)

for i in range(2):
    player.move_forward()

player.turn_right()

for i in range(4):
    player.move_forward()

player.turn_left()

for i in range(2):
    player.move_forward()

wait_quit()
