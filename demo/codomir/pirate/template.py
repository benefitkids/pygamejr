from codomir import player, set_map, wait_quit, maps

set_map(maps.pirates.template)

player.move_forward()
# player.turn_right()
player.move_forward()
player.move_forward()

wait_quit()
