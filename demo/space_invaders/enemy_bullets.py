import time
import pygamejr

# снаряды
bullets = []

#время перезарядки
RELOAD_TIME = 0.5

#время последнего выстрела
last_fire_time = 0

def fire(gun_sprite):
    """
    Выстрел пулей
    :param gun_sprite: спрайт, который стреляет
    """
    global last_fire_time  # 4
    time_now = time.time()

    if time_now - last_fire_time >= RELOAD_TIME:
        is_reloading = False
    else:
        is_reloading = True

    # "выстрел" - добавление нового снаряда в общий список
    if not is_reloading:
        bullet = pygamejr.CircleSprite(color="white", radius=3)
        bullet.rect.centerx = gun_sprite.rect.centerx
        bullet.rect.bottom = gun_sprite.rect.top
        bullets.append(bullet)
        last_fire_time = time_now

BULLET_SPEED = 3
def fly():
    """
    Полёт пули
    """
    bullet_for_delete = None

    for bullet in bullets:
        bullet.rect.y += BULLET_SPEED
        if bullet.rect.y >= pygamejr.screen.get_height():
            bullet_for_delete = bullet

    if bullet_for_delete:
        bullet_for_delete.kill()
        bullet_for_delete.is_visible = False
        bullets.remove(bullet_for_delete)

def is_hit_enemy(enemy_sprite):  # 5
   """
   Простая функция проверки, попала ли пуля во врага.
   :param enemy_sprite: спрайт врага
   :return: True если одна из пуль попала во врага, False если ни одна пуля не попала.
   """

   for bullet in bullets:
       if bullet.rect.colliderect(enemy_sprite):
           bullet.is_visible = False
           bullets.remove(bullet)
           return True
   return False