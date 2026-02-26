import pygame
import pygamejr

# --- Сцена меню ---
menu_scene = pygamejr.Scene()
pygamejr.set_scene(menu_scene)

title = pygamejr.TextSprite("Меню", size=64)
title.rect.center = (400, 220)

hint = pygamejr.TextSprite("Нажми ПРОБЕЛ чтобы начать", size=28)
hint.rect.center = (400, 320)

# --- Сцена игры ---
game_scene = pygamejr.Scene()
pygamejr.set_scene(game_scene)

bee = pygamejr.ImageSprite(pygamejr.resources.image.bee)
bee.rect.center = (100, 300)

back_hint = pygamejr.TextSprite("ESC — вернуться в меню", size=24)
back_hint.rect.bottomleft = (10, 590)

# Начинаем с меню
pygamejr.set_scene(menu_scene)

prev_space = False
prev_esc = False

for dt in pygamejr.every_frame():
    keys = pygame.key.get_pressed()
    current_scene = pygamejr.get_current_scene()

    # Переход в игру
    if keys[pygame.K_SPACE] and not prev_space:
        if current_scene is menu_scene:
            pygamejr.set_scene(game_scene)

    # Возврат в меню
    if keys[pygame.K_ESCAPE] and not prev_esc:
        if current_scene is game_scene:
            pygamejr.set_scene(menu_scene)

    # Движение пчелы в игровой сцене
    if pygamejr.get_current_scene() is game_scene:
        bee.rect.x += 150 * dt
        if bee.rect.left > pygamejr.screen.get_width():
            bee.rect.right = 0

    prev_space = keys[pygame.K_SPACE]
    prev_esc = keys[pygame.K_ESCAPE]
