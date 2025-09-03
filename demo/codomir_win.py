from codomir import player, set_map, wait_quit, resources

set_map(resources.map1)

for i in range(5):
    player.move_forward()

wait_quit()
