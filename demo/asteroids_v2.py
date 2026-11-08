"""Asteroids: вариант с поворотом контура через Vector2.

W/S — вперёд/назад, A/D — поворот, пробел — стрельба.
Запуск из корня проекта: python demo/asteroids_v2.py
"""

import random

import pygame
import pygamejr
from pygamejr.sprite.base import BaseSprite


# Формы: BrickSigma/Asteroids-pygame, Asteroids/assets/sprites.py.
METEOR_SHAPES = [
    [(23, 0), (72, 12), (79, 46), (64, 71), (25, 79), (0, 51), (0, 18)],
    [(25, 0), (79, 24), (79, 54), (46, 79), (2, 61), (0, 19)],
    [(25, 2), (66, 0), (79, 38), (67, 63), (38, 79), (14, 69), (0, 20)],
]


class Player(BaseSprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.FRect(0, 0, 44, 48)
        self.rect.center = (x, y)
        self.speed = 150
        self.rotation = 0
        self.rotation_speed = 180
        self.points = [(0, -24), (-22, 22), (0, 10), (22, 22)]

    def direction(self):
        return pygame.Vector2(0, -1).rotate(self.rotation)

    def update(self, dt=0):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rotation -= self.rotation_speed * dt
        if keys[pygame.K_d]:
            self.rotation += self.rotation_speed * dt
        self.rotation %= 360

        rotated = [pygame.Vector2(point).rotate(self.rotation) for point in self.points]
        center = self.rect.center
        self.rect.size = (
            2 * max(abs(point.x) for point in rotated) + 2,
            2 * max(abs(point.y) for point in rotated) + 2,
        )
        self.rect.center = center

        distance = 0
        if keys[pygame.K_w]:
            distance += self.speed * dt
        if keys[pygame.K_s]:
            distance -= self.speed * dt
        movement = self.direction() * distance
        self.rect.x += movement.x
        self.rect.y += movement.y
        self.rect.clamp_ip(pygamejr.screen.get_frect())

    def draw(self, draw_rect=False):
        if not self.is_visible:
            return
        points = []
        for point in self.points:
            offset = pygame.Vector2(point).rotate(self.rotation)
            points.append(pygame.Vector2(self.rect.center) + offset)
        pygame.draw.lines(pygamejr.screen, "white", True, points, 2)
        if draw_rect:
            pygame.draw.rect(pygamejr.screen, "red", self.rect, 1)


class Meteor(BaseSprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.FRect(0, 0, 50, 50)
        self.rect.center = (x, y)
        self.speed_x = random.uniform(-70, 70)
        self.speed_y = random.uniform(50, 100)

        shape = random.choice(METEOR_SHAPES)
        self.points = []
        for point_x, point_y in shape:
            self.points.append((point_x * 0.6 + 1, point_y * 0.6 + 1))

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

    def draw(self, draw_rect=False):
        if not self.is_visible:
            return

        points = []
        for point_x, point_y in self.points:
            points.append((self.rect.x + point_x, self.rect.y + point_y))
        pygame.draw.lines(pygamejr.screen, "white", True, points, 2)

        if draw_rect:
            pygame.draw.rect(pygamejr.screen, "red", self.rect, 1)


class Bullet(BaseSprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.direction = pygame.Vector2(direction).normalize()
        self.rect = pygame.FRect(
            0, 0,
            abs(self.direction.x) * 12 + 3,
            abs(self.direction.y) * 12 + 3,
        )
        self.rect.center = (x, y)
        self.speed = 500

    def update(self, dt=0):
        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * self.speed * dt
        if not self.rect.colliderect(pygamejr.screen.get_frect()):
            self.kill()

    def draw(self, draw_rect=False):
        if not self.is_visible:
            return
        center = pygame.Vector2(self.rect.center)
        pygame.draw.line(
            pygamejr.screen, "yellow",
            center - self.direction * 6, center + self.direction * 6, 3,
        )
        if draw_rect:
            pygame.draw.rect(pygamejr.screen, "red", self.rect, 1)


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
        direction = player.direction()
        position = pygame.Vector2(player.rect.center) + direction * 30
        bullet = Bullet(position.x, position.y, direction)
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
