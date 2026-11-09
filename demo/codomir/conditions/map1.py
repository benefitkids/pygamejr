from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map1)

# First choice: push or step forward.
# Reach the coin in two steps: if there is a box ahead, push it;
# otherwise, step forward. Check the adjacent cell again before each action.
# Write two if/else blocks in sequence, without for or while loops:
# this exercise teaches you to choose an action.
# Before running the code, predict which branch each check will take.
# Then use Tiled to remove the box, and in another variant put it on the coin.
# For each variant, predict both branches again and run the same code.
# Hint: after a push, the hero occupies the box's previous cell,
# and the box is still ahead. If there is no box, the check returns False.
# A box on the coin does not win the game: the hero must reach the coin.

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

wait_quit()
