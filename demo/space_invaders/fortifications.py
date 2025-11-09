import pygamejr
import bullets
import enemy_bullets

fortifications = []
for bottom in range(70, 110, 15):
   for left in range(100, pygamejr.screen.get_width() - 100, 150):
       fortification = pygamejr.RectSprite(width=50, height=10)
       fortification.rect.bottom = pygamejr.screen.get_height() - bottom
       fortification.rect.left = left
       fortifications.append(fortification)

def is_hit_by_bullet():
   '''проверяет попала ли наша пуля в укрепление'''
   for fortification in fortifications:
       if bullets.is_hit_enemy(fortification):
           fortification.is_visible = False
           fortifications.remove(fortification)
           return True
   return False

def is_hit_by_enemy_bullet():
   '''проверяет попала ли вражеская пуля в укрепление'''
   for fortification in fortifications:
       if enemy_bullets.is_hit_enemy(fortification):
           fortification.is_visible = False
           fortifications.remove(fortification)
           return True
   return False
