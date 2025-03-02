import pygamejr

ball = pygamejr.CircleSprite()
bee = pygamejr.ImageSprite(pygamejr.resources.image.bee)
bee.rect.centerx = pygamejr.screen.get_width() / 2
bee.rect.centery = pygamejr.screen.get_height() / 2

for frame in pygamejr.every_frame():
    ball.rect.x += 1
    bee.rect.x += 1
    ball.draw()
    bee.draw()
