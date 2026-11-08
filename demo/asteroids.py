"""Игра из урока docs/lessons/pygamejr-classes-asteroids.md.

W/S — вперёд/назад, A/D — поворот.
Пробел — стрельба.
Запуск из корня проекта: python demo/asteroids.py
"""

import random

import pygame
import pygamejr


# Формы: BrickSigma/Asteroids-pygame, Asteroids/assets/sprites.py.
METEOR_SHAPES = [
    [(23, 0), (72, 12), (79, 46), (64, 71), (25, 79), (0, 51), (0, 18)],
    [(25, 0), (79, 24), (79, 54), (46, 79), (2, 61), (0, 19)],
    [(25, 2), (66, 0), (79, 38), (67, 63), (38, 79), (14, 69), (0, 20)],
]


class Player(pygamejr.ImageSprite):
    def __init__(self, x, y):
        # Рисуем корабль носом вниз: это направление move_forward() при угле 0.
        image = pygame.Surface((46, 50), pygame.SRCALPHA)
        points = [(23, 48), (1, 2), (23, 14), (45, 2)]
        pygame.draw.lines(image, "white", True, points, 2)
        super().__init__(image=image, sprite_angle=180)
        self.rect.center = (x, y)
        self.speed = 150
        self.rotation_speed = 180

    def update(self, dt=0):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rotate(self.rotation_speed * dt)
        if keys[pygame.K_d]:
            self.rotate(-self.rotation_speed * dt)
        if keys[pygame.K_w]:
            self.move_forward(self.speed * dt)
        if keys[pygame.K_s]:
            self.move_forward(-self.speed * dt)
        self.rect.clamp_ip(pygamejr.screen.get_frect())


class Meteor(pygamejr.ImageSprite):
    def __init__(self, x, y):
        image = pygame.Surface((50, 50), pygame.SRCALPHA)
        shape = random.choice(METEOR_SHAPES)
        points = []
        for point_x, point_y in shape:
            points.append((point_x * 0.6 + 1, point_y * 0.6 + 1))
        pygame.draw.lines(image, "white", True, points, 2)
        super().__init__(image=image)
        self.rect.center = (x, y)
        self.speed_x = random.uniform(-70, 70)
        self.speed_y = random.uniform(50, 100)

    def update(self, dt=0):
        self.rect.x += self.speed_x * dt
        self.rect.y += self.speed_y * dt

        width, height = pygamejr.screen.get_size()

        if self.rect.top > height:
            self.rect.bottom = 0

        if self.rect.left > width:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = width


class Bullet(pygamejr.ImageSprite):
    def __init__(self, x, y, angle):
        image = pygame.Surface((4, 12), pygame.SRCALPHA)
        pygame.draw.line(image, "yellow", (2, 0), (2, 11), 3)
        super().__init__(image=image, sprite_angle=angle)
        self.rect.center = (x, y)
        self.speed = 500
        self.move_forward(30)  # Переносим пулю из центра корабля к носу.

    def update(self, dt=0):
        self.move_forward(self.speed * dt)
        if not self.rect.colliderect(pygamejr.screen.get_frect()):
            self.kill()


player = Player(
    pygamejr.screen.get_width() / 2,
    pygamejr.screen.get_height() - 70,
)

meteors = []
width, height = pygamejr.screen.get_size()

for i in range(6):
    x = random.randint(50, width - 50)
    y = random.randint(50, height // 2)
    meteor = Meteor(x, y)
    meteors.append(meteor)

bullets = []
reload_time = 0.25
cooldown = 0
score = 0

for dt in pygamejr.every_frame():
    cooldown = max(0, cooldown - dt)
    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE] and cooldown == 0:
        bullet = Bullet(player.rect.centerx, player.rect.centery, player.angle)
        bullets.append(bullet)
        cooldown = reload_time

    bullets = [bullet for bullet in bullets if bullet.alive()]

    for bullet in bullets[:]:
        for meteor in meteors[:]:
            if bullet.rect.colliderect(meteor.rect):
                bullet.kill()
                meteor.kill()
                bullets.remove(bullet)
                meteors.remove(meteor)
                score += 1
                print("Уничтожено метеоритов:", score)
                break

    game_over = False
    for meteor in meteors:
        if player.rect.colliderect(meteor.rect):
            game_over = True
            break

    if game_over:
        print("Поражение! Уничтожено метеоритов:", score)
        break

    if not meteors:
        print("Победа! Все метеориты уничтожены.")
        break

pygame.quit()
