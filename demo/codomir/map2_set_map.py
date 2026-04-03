from time import sleep

from codomir import set_map, maps

set_map(maps.linear.map2)

# Just wait 2 seconds without redrawing the screen
# to see what set_map has drawn.
sleep(2)
