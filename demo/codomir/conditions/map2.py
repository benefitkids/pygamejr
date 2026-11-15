from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map2)

# Step forward once, then push twice to reach the coin on the main layout.
# A push moves both the hero and the box; the box remains directly ahead.
# The separate conditional teacher solution in the lesson uses three
# sequential if/else checks, without loops. Predict False, True, True.
# Use that conditional solution for variants in Tiled: remove the box,
# move it next to the hero, or put it on the coin. Predict all three checks
# before each run; the direct commands below solve only the main layout.
# A box on the coin does not win the game: the hero must reach the coin.

player.move_forward()

player.push()
player.push()

wait_quit()
