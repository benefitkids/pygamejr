import pygamejr

ball = pygamejr.CircleSprite()
bee = pygamejr.ImageSprite(pygamejr.resources.image.bee)
bee.rect.centerx = pygamejr.screen.get_width() / 2
bee.rect.centery = pygamejr.screen.get_height() / 2

while pygamejr.next_frame():
    ball.rect.x += 0.5
    bee.rect.x += 0.5
