import time
import pygamejr
import pygame

tank = pygamejr.ImageSprite(pygamejr.resources.image_tanks.tank_green)
tank.rect.centerx = pygamejr.screen.get_width() / 2
tank.rect.centery = pygamejr.screen.get_height() / 2

tree = pygamejr.ImageSprite(pygamejr.resources.image_tanks.tree_green)
tree.rect.centerx = pygamejr.screen.get_width() / 4
tree.rect.centery = pygamejr.screen.get_height() / 4

for frame in pygamejr.every_frame(draw_sprites_rect=True):

    keys = pygame.key.get_pressed()

    rect = tank.rect.copy()
    if keys[pygame.K_w]:
        tank.move_forward()
    if keys[pygame.K_s]:
        tank.move_forward(-1)

    if tank.rect.colliderect(tree.rect):
        tank.rect = rect

    if keys[pygame.K_a]:
        tank.turn_right()
    if keys[pygame.K_d]:
        tank.turn_left()

    if tank.rect.colliderect(tree.rect):
        if keys[pygame.K_a]:
            tank.turn_left()
        if keys[pygame.K_d]:
            tank.turn_right()