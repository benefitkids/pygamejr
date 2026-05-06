import pygame
import pygamejr

player = pygamejr.ImageSprite(pygamejr.resources.image.bee)
player.rect.center = (pygamejr.screen.get_width() // 2, pygamejr.screen.get_height() // 2)

pygamejr.show_joystick()
pygamejr.show_action_button(pygame.K_SPACE, label="A", mode='tap')
pygamejr.show_action_button(pygame.K_LSHIFT, label="B", mode='hold')

for dt in pygamejr.every_frame():
    keys = pygamejr.key.get_pressed()
    speed = 200 * dt
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        player.rect.y -= speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        player.rect.y += speed
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player.rect.x -= speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player.rect.x += speed
