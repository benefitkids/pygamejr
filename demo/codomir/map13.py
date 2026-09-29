from codomir import player, wait_quit, set_map, maps

set_map(maps.linear.map13)

player.turn_left()
player.turn_left()
player.move_forward()
player.move_forward()
player.move_forward()
player.turn_right()
player.move_forward()
player.move_forward()
player.move_forward()

wait_quit()
