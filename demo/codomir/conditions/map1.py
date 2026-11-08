from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map1)

# Дойдите до монеты: если впереди ящик, толкните его, иначе шагните.
# Перед запуском предскажите, какая ветвь выполнится при каждой проверке.
# Подсказка: после толчка ящик всё ещё перед героем.

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

wait_quit()
