from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map3)

# Repeat twice: turn right, then push three cells.
# The hero starts facing right, so the passages lead down and then left.
# Each push moves the hero too; the second passage ends at the coin.
# The conditional teacher solution also handles the box variants.

for i in range(2):
    player.turn_right()
    for i in range(3):
        player.push()

wait_quit()
