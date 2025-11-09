import time
import pygamejr
import pygame

tank = pygamejr.ImageSprite(pygamejr.resources.image_tanks.tank_green)
tank.rect.centerx = pygamejr.screen.get_width() / 2
tank.rect.centery = pygamejr.screen.get_height() / 2

tree = pygamejr.ImageSprite(pygamejr.resources.image_tanks.tree_green)


for frame in pygamejr.every_frame():

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



