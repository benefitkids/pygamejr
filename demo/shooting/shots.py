import time
import pygamejr
import pygame

# корабль
ship = pygamejr.ImageSprite("../assets/Ship.png")
ship.rect.bottom = pygamejr.screen.get_height() - 50

# враг
enemy = pygamejr.ImageSprite("../assets/InvaderA_00.png")

###Логика пуль#########



for frame in pygamejr.every_frame():
    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE]:
        fire(ship)

    if enemy.is_visible and is_hit_enemy(enemy):
        enemy.is_visible = False

    bullet_fly()