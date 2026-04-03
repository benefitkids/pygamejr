# Run from repo root: py demo/8set_image.py
import pygame
import pygamejr
from pygamejr.resources import image as img

SPRITES = [img.bee, img.frog, img.ladybug]
idx = 0

hero = pygamejr.ImageSprite(SPRITES[idx])
hero.rect.center = (
    pygamejr.screen.get_width() / 2,
    pygamejr.screen.get_height() / 2,
)

for _ in pygamejr.every_frame():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            idx = (idx + 1) % len(SPRITES)
            hero.set_image(filename=SPRITES[idx])
