import pygamejr
import pygame
import bullets
import enemies
import fortifications
import enemy_bullets

# корабль
ship = pygamejr.ImageSprite('../assets/Ship.png')
ship.rect.bottom = pygamejr.screen.get_height() - 50


for frame in pygamejr.every_frame():
    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE]:
        bullets.fire(ship)

    if keys[pygame.K_d] and ship.rect.right <= pygamejr.screen.get_width():
        ship.rect.centerx += 3

    if keys[pygame.K_a] and ship.rect.left >= 0:
        ship.rect.centerx -= 3

    enemies.is_hit_enemy_by_bullet()
    enemies.move_vertically()
    enemies.move_horizontally()

    bullets.fly()

    fortifications.is_hit_by_bullet()
    fortifications.is_hit_by_enemy_bullet()

    enemies.fire()
    enemy_bullets.fly()

