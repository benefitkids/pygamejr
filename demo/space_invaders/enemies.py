import random
import pygamejr
import bullets
import enemy_bullets

# враги
enemies = []
for top in range(50, 200, 50):
   for left in range(100, pygamejr.screen.get_width() - 100, 50):
       enemy = pygamejr.ImageSprite("../assets/InvaderA_00.png")
       enemy.rect.top = top
       enemy.rect.left = left
       enemies.append(enemy)

vertical_speed = 0.1

def move_vertically():
    '''Движение врагов по вертикали'''
    for enemy in enemies:
        enemy.rect.centery += vertical_speed
        if enemy.rect.centery >= pygamejr.screen.get_height()-200:
            print('game over')

horizontal_speed = 0.5
horizontal_limit = 0

def move_horizontally():
   '''Движение врагов по горизонтали'''
   global horizontal_speed
   global horizontal_limit
   for enemy in enemies:
       enemy.rect.centerx += horizontal_speed

   horizontal_limit += horizontal_speed
   if horizontal_limit > 80 or horizontal_limit == 0:
       horizontal_speed *= -1

def is_hit_enemy_by_bullet():
   '''проверяет попали ли пуля во врага'''
   for enemy in enemies:
       if bullets.is_hit_enemy(enemy):
           enemy.is_visible = False
           enemies.remove(enemy)
           return True
   return False

def fire():
    if enemies:
        enemy = random.choice(enemies)
        enemy_bullets.fire(enemy)
