import pygamejr

bee = pygamejr.ImageSprite(pygamejr.resources.image.bee)

for dt in pygamejr.every_frame():
    bee.rect.x += 0.5
