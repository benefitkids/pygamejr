import pygamejr

bee = pygamejr.ImageSprite(pygamejr.resources.image.bee)
frog = pygamejr.ImageSprite(pygamejr.resources.image.frog)
frog.is_visible = False
frog.rect.x = 100

pygamejr.wait_quit()