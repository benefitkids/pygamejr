import pygamejr

text = pygamejr.TextSprite("Hello World!", 48)
text.rect.center = (400, 300)

pygamejr.wait_quit()
