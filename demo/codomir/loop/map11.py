from codomir import player, wait_quit, set_map, maps

set_map(maps.loop.map11)

for i in range(3):
    player.turn_left()
    player.move_forward()
    player.move_forward()

player.move_forward()
player.turn_left()
player.move_forward()
player.turn_right()
player.move_forward()
player.turn_left()
player.move_forward()
player.move_forward()

for i in range(2):
    player.move_forward()
    player.move_forward()
    player.turn_left()

for i in range(2):
    player.move_forward()
    player.turn_right()
    player.move_forward()

player.turn_left()
player.move_forward()

wait_quit()
