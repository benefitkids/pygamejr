from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map3)

# Reach the coin along two short passages, turning right at the corner.
# Use four if/else checks in sequence, without for or while loops.
# Before running, predict each branch, including the first check after turning.
# In Tiled, try removing either box, removing both, or moving the first
# box to the corner. Run the same code for every variant.
# Hint: ahead means the cell in the direction the hero is facing.
# Teacher: after a push the box is still ahead; after turning, check the new direction.

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

player.turn_right()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

wait_quit()
