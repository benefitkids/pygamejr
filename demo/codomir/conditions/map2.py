from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map2)

# Check again after pushing.
# Reach the coin in three steps. Before each step, check for a box:
# push if there is one ahead; otherwise, move forward.
# Write three if/else blocks in sequence, without for or while loops.
# Before running the code, predict which branch each check will take.
# What will the next check return after the first push? Explain why.
# Hint: a push moves both the hero and the box forward by one cell.
# The hero takes the box's previous cell, so the box is still ahead.
# Always check again: the first result does not describe the whole route.
# In Tiled, try removing the box, moving it next to the hero, or putting
# it on the coin. Predict all three checks and run the same code each time.
# A box on the coin does not win the game: the hero must reach the coin.

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

wait_quit()
