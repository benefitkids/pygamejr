from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map1)

# Push twice to reach the coin. Each push moves both the hero and the box.
# The conditional teacher version checks twice and also handles a missing box
# or a box moved onto the coin (2, 3).

player.push()
player.push()

wait_quit()
