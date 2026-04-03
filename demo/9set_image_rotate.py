# Run from repo root: py demo/9set_image_rotate.py
# Rotated sprite + Space cycles texture; mask collision with a tree (compare with demo/collidemask.py).
import pygame
import pygamejr

SKINS = [
    pygamejr.resources.image_tanks.tank_green,
    pygamejr.resources.image_tanks.tank_blue,
]

tank = pygamejr.ImageSprite(SKINS[0])
tank.rect.centerx = pygamejr.screen.get_width() / 2
tank.rect.centery = pygamejr.screen.get_height() / 2
for _ in range(45):
    tank.turn_right()

skin_idx = 0

tree = pygamejr.ImageSprite(pygamejr.resources.image_tanks.tree_green)

for _ in pygamejr.every_frame():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            print("SPACE")
            skin_idx = (skin_idx + 1) % len(SKINS)
            tank.set_image(filename=SKINS[skin_idx])

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        tank.turn_right()
    if keys[pygame.K_d]:
        tank.turn_left()

    if pygame.sprite.collide_mask(tank, tree):
        if keys[pygame.K_a]:
            tank.turn_left()
        if keys[pygame.K_d]:
            tank.turn_right()

    rect = tank.rect.copy()
    if keys[pygame.K_w]:
        tank.move_forward()
    if keys[pygame.K_s]:
        tank.move_forward(-1)

    if pygame.sprite.collide_mask(tank, tree):
        tank.rect = rect
