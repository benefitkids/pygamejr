import pygame
import pygamejr

bee = pygamejr.ImageSprite(pygamejr.resources.image.bee)

SPEED = 5

for frame in pygamejr.every_frame():

    # Получаем состояние всех клавиш
    keys = pygame.key.get_pressed()

    # Двигаем пчелу в зависимости от нажатых клавиш
    if keys[pygame.K_w]:
        new_top = bee.rect.top - SPEED
        if new_top > 0:
            bee.rect.top = new_top
    if keys[pygame.K_s]:
        new_bottom = bee.rect.bottom + SPEED
        if new_bottom < pygamejr.screen.get_height():
            bee.rect.bottom = new_bottom
    if keys[pygame.K_a]:
        new_left = bee.rect.left - SPEED
        if new_left > 0:
            bee.rect.left = new_left
    if keys[pygame.K_d]:
        new_right = bee.rect.right + SPEED
        if new_right < pygamejr.screen.get_width():
            bee.rect.right = new_right
