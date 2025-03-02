import pygamejr

width = pygamejr.screen.get_width()
height = pygamejr.screen.get_height()

top_left = pygamejr.ImageSprite(pygamejr.resources.image.coin_gold)
top_left.rect.top = 0
top_left.rect.left = 0

top_right = pygamejr.ImageSprite(pygamejr.resources.image.coin_bronze)
top_right.rect.top = 0
top_right.rect.right = width

bottom_left = pygamejr.ImageSprite(pygamejr.resources.image.coin_gold)
bottom_left.rect.bottom = height
bottom_left.rect.left = 0

bottom_right = pygamejr.ImageSprite(pygamejr.resources.image.coin_gold)
bottom_right.rect.bottom = height
bottom_right.rect.right = width

center = pygamejr.ImageSprite(pygamejr.resources.image.coin_silver)
center.rect.centerx = pygamejr.screen.get_width() / 2
center.rect.centery = pygamejr.screen.get_height() / 2

for frame in pygamejr.every_frame():
    top_left.draw()
    top_right.draw()
    bottom_left.draw()
    bottom_right.draw()
    center.draw()
