import pygame
import pygamejr

bee = pygamejr.ImageSprite(pygamejr.resources.image.bee)
slime = pygamejr.ImageSprite(pygamejr.resources.image.slime_block)
slime.rect.centerx = pygamejr.screen.get_width()/2
slime.rect.centery = pygamejr.screen.get_height()/2

SPEED= 5

for frame in pygamejr.every_frame():
    # Получаем состояние всех клавиш
    keys = pygame.key.get_pressed()

    # Создадим копию прямоугольника описывающего спрайт
    rect = bee.rect.copy()
    # Двигаем прямоугольник в зависимости от нажатых клавиш
    if keys[pygame.K_w]:
        rect.centery -= SPEED
    if keys[pygame.K_s]:
        rect.centery += SPEED
    if keys[pygame.K_a]:
        rect.centerx -= SPEED
    if keys[pygame.K_d]:
        rect.centerx += SPEED

    # Обновим положение пчелки только если пчелка не касается слфайм
    if not slime.rect.colliderect(rect):
        bee.rect.update(rect)
