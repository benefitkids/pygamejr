# Условия: заметить ящик и выбрать действие

Урок по условиям: десять карт `maps.conditions.map1`–`map10`.
Цель каждой карты — довести **героя до монеты**. Ящики мешают пройти: их можно толкать.
Расстановка ящиков после прохождения помогает проверить программу, но не является отдельной целью игры.

Вы уже знакомы с последовательностью команд и циклом `for i in range(...)`.
На картах 1–3 временно оставим циклы в стороне, чтобы разобраться в самом выборе действия.
На карте 4 свернём повторяющиеся проверки в знакомый цикл; карты 4–6 используют простые циклы,
а карты 7–10 — более сложные маршруты, где допустимы вложенные циклы.

## Что сообщает датчик

`player.is_box_ahead()` возвращает значение типа `bool`:

| Значение | Что сейчас находится в соседней клетке перед героем |
| --- | --- |
| `True` | Ящик |
| `False` | Ящика нет |

Вызов только проверяет клетку: он не двигает героя и не толкает ящик.
«Впереди» зависит от направления взгляда. После `player.turn_right()` или
`player.turn_left()` датчик смотрит уже в новом направлении.

Условие `if` выбирает действие по результату проверки. Выполняется ровно одна ветка:

```python
if player.is_box_ahead():
    player.push()
else:
    player.move_forward()
```

Двоеточие начинает ветку, отступ в четыре пробела показывает её команды.
При `True` выполняется `push()`, при `False` — `move_forward()`.
Этот блок подходит для проходов наших карт: при правильном числе шагов перед героем
будет свободная клетка или ящик с местом для толкания.

**Датчик сообщает наличие ящика, а не возможность толкнуть его.** За ящиком может
быть стена, край карты или другой ящик. Результат `False` тоже не гарантирует
свободный путь: перед героем может быть стена. Поэтому важно изучить маршрут и число шагов.

## Что меняется после толчка

Один `player.push()` сдвигает ящик на клетку и одновременно переводит героя на прежнее
место ящика. В прямом проходе ящик остаётся непосредственно перед героем.
Если сразу выполнить `player.move_forward()`, герой столкнётся с ним.
Перед следующим действием нужно **снова** вызвать датчик.

Например, на карте 1 две проверки выполняются последовательно, без циклов:

```python
if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()
```

На основной расстановке обе проверки дают `True`. После первого толчка ящик
занимает клетку с монетой, но победы ещё нет. После второго герой сам входит
на монету и побеждает. Если убрать ящик, тот же код дважды выберет `else`.
Так условие приспосабливает программу к миру, даже если команд в тексте стало больше.

На карте 2 первая проверка даст `False`, затем две проверки дадут `True`:
первый шаг приближает героя к ящику, а после толчка ящик всё ещё впереди.
На карте 3 после двух таких проверок нужен поворот и ещё две новые проверки:

```python
player.turn_right()
if player.is_box_ahead():
    player.push()
else:
    player.move_forward()
```

Это фрагмент середины маршрута карты 3. Результат до поворота нельзя использовать
вместо новой проверки после него: соседняя клетка теперь другая.

## Ошибки и новая попытка

Игра заканчивается поражением (`player.is_game_over`), если:

- вызвать `player.push()`, когда впереди нет ящика;
- толкать ящик в стену, за край карты или в другой ящик;
- вызвать `player.move_forward()` в ящик, стену или за край карты.

При неудачном толчке герой и ящик остаются на своих клетках. Для новой попытки
выполните сброс перед исправленным решением:

```python
player.reset()
```

Сброс восстанавливает начальные ящики выбранной карты, возвращает героя на старт
лицом вправо и снимает состояние победы или поражения. `set_map(...)` выбирает другую карту.

## Как работать с картами

Сначала прочитайте схему, предскажите результаты датчика и запишите программу.
После запуска сравните предсказание с действиями героя. Решения преподавателя находятся
после каталога; открывайте их после собственной попытки.

Каждая схема ниже имеет ровно 8 строк по 8 клеток. `#` — стена, `.` — пол,
`>` — герой на старте, лицом вправо, `B` — ящик, `F` — монета (клетка Win).
Координаты `(x, y)` считаются с нуля от левого верхнего угла; `x` растёт вправо, `y` вниз.
Пустая клетка за концом прохода — карман для ящика: герой останавливается раньше,
на повороте или монете. Карман — обычный пол, не специальная цель.

Для проверки переносимости откройте **копию** TMX в Tiled и меняйте только ящики
в слое `boxes`, сохраняя пол, стены, старт и монету. Загрузите копию через
`set_map("path/to/variant.tmx")`, оставив решающую часть программы прежней.
Варианты каждого упражнения перечислены ниже. Выбирайте действие по датчику,
а не по номеру шага `i`: после перестановки ящика номер шага до встречи изменится.

## Каталог упражнений

### Карта 1. Первый выбор: толкнуть или шагнуть

```text
########
########
########
>BF.####
########
########
########
########
```

**Учебная цель:** Научиться выбирать между двумя действиями по значению `bool`.

**Задание:** Доведите героя до монеты за два продвижения. Напишите два последовательных блока `if/else`, без `for` и `while`.

**Подсказка:** После успешного толчка ящик всё ещё перед героем.

**Проверка тем же кодом:** уберите ящик; затем в отдельной копии поставьте его на монету `(2, 3)`. Перед каждым запуском предскажите ветки.

### Карта 2. Проверь ещё раз после толчка

```text
########
########
########
>.BF.###
########
########
########
########
```

**Учебная цель:** Замечать изменение результата датчика после шага и повторять проверку после толчка.

**Задание:** Доведите героя до монеты за три продвижения. Напишите три последовательных блока `if/else`, без `for` и `while`.

**Подсказка:** Сначала посмотрите, сколько свободных клеток отделяет старт от ящика.

**Проверка тем же кодом:** уберите ящик; затем отдельно поставьте его рядом со стартом `(1, 3)` или на монету `(3, 3)`. Перед каждым запуском предскажите ветки.

### Карта 3. Новое направление после поворота

```text
########
#>B..###
###B####
###F####
###.####
########
########
########
```

**Учебная цель:** Проверять соседнюю клетку заново после смены направления.

**Задание:** Пройдите два коротких прохода с правым поворотом. Используйте четыре последовательных блока `if/else` и поворот, без `for` и `while`.

**Подсказка:** После поворота «впереди» означает соседнюю клетку снизу.

**Проверка тем же кодом:** уберите первый ящик, второй или оба; затем отдельно перенесите первый на угол `(3, 1)`, оставив второй на месте. Перед каждым запуском предскажите ветки.

### Карта 4. Поворот налево

```text
######.#
######F#
######.#
######B#
######.#
######.#
######.#
>.B.....
```

**Учебная цель:** Поместить повторяющийся блок `if/else` в знакомый простой цикл `for`.

**Задание:** Пройдите шесть клеток вправо, поверните налево и пройдите шесть клеток вверх. Для каждого прохода используйте простой цикл с проверкой внутри.

**Подсказка:** Считайте продвижения героя: толчок тоже продвигает его на одну клетку.

**Проверка тем же кодом:** поставьте первый ящик в `(1, 7)`, затем в отдельной копии в `(5, 7)`. Другие ящики оставьте на месте. Перед каждым запуском предскажите ветки.

**Разбор после предсказания:** фактическая трасса первого простого цикла на основной расстановке. Итерации пронумерованы с 1; в `range` счётчик начинается с 0.

| Итерация | `is_box_ahead()` | Выбранное действие |
| --- | --- | --- |
| 1 | `False` | `player.move_forward()` |
| 2 | `True` | `player.push()` |
| 3 | `True` | `player.push()` |
| 4 | `True` | `player.push()` |
| 5 | `True` | `player.push()` |
| 6 | `True` | `player.push()` |

В одном и том же цикле встречаются обе ветки: сначала герой идёт по свободным клеткам, затем толкает. Проверка выполняется заново на каждой итерации.

### Карта 5. Три прохода

```text
>..B....
######.#
######B#
######.#
######.#
.FB....#
######.#
########
```

**Учебная цель:** Разбить маршрут на три прохода и проверять датчик внутри каждого цикла.

**Задание:** Пройдите участки длиной 6, 5 и 5 клеток с правыми поворотами. Используйте простые циклы, проверяя клетку на каждой итерации.

**Подсказка:** На углу заканчивается один проход и начинается следующий.

**Проверка тем же кодом:** поставьте первый ящик в `(1, 0)`, затем в отдельной копии в `(5, 0)`. Другие ящики оставьте на месте. Перед каждым запуском предскажите ветки.

**Разбор после предсказания:** фактическая трасса первого простого цикла на основной расстановке. Итерации пронумерованы с 1; в `range` счётчик начинается с 0.

| Итерация | `is_box_ahead()` | Выбранное действие |
| --- | --- | --- |
| 1 | `False` | `player.move_forward()` |
| 2 | `False` | `player.move_forward()` |
| 3 | `True` | `player.push()` |
| 4 | `True` | `player.push()` |
| 5 | `True` | `player.push()` |
| 6 | `True` | `player.push()` |

В одном и том же цикле встречаются обе ветки: сначала герой идёт по свободным клеткам, затем толкает. Проверка выполняется заново на каждой итерации.

### Карта 6. П-образный склад

```text
>.B.....
######.#
######.#
######.#
######B#
######.#
.F.B...#
######.#
```

**Учебная цель:** Выбрать число повторений отдельно для каждого прямого прохода.

**Задание:** Пройдите участки длиной 6, 6 и 5 клеток с правыми поворотами. Используйте простые циклы без вложенности.

**Подсказка:** Последний проход короче первых двух.

**Проверка тем же кодом:** поставьте первый ящик в `(1, 0)`, затем в отдельной копии в `(5, 0)`. Другие ящики оставьте на месте. Перед каждым запуском предскажите ветки.

**Разбор после предсказания:** фактическая трасса первого простого цикла на основной расстановке. Итерации пронумерованы с 1; в `range` счётчик начинается с 0.

| Итерация | `is_box_ahead()` | Выбранное действие |
| --- | --- | --- |
| 1 | `False` | `player.move_forward()` |
| 2 | `True` | `player.push()` |
| 3 | `True` | `player.push()` |
| 4 | `True` | `player.push()` |
| 5 | `True` | `player.push()` |
| 6 | `True` | `player.push()` |

В одном и том же цикле встречаются обе ветки: сначала герой идёт по свободным клеткам, затем толкает. Проверка выполняется заново на каждой итерации.

### Карта 7. Склад с левыми поворотами

```text
######.#
.F..B..#
######.#
######.#
######B#
######.#
######.#
>...B...
```

**Учебная цель:** Повторить одинаковые по длине проходы с поворотами с помощью вложенного цикла.

**Задание:** Пройдите участки длиной 6, 6 и 5 клеток с левыми поворотами. Объедините два одинаковых участка внешним циклом.

**Подсказка:** Вместе с длинным проходом повторяется и поворот в его конце.

**Проверка тем же кодом:** поставьте первый ящик в `(1, 7)`, затем в отдельной копии в `(5, 7)`. Другие ящики оставьте на месте. Перед каждым запуском предскажите ветки.

**Разбор после предсказания:** фактическая трасса первого вызова внутреннего цикла (внешняя итерация `i = 0`) на основной расстановке. Итерации пронумерованы с 1; в `range` счётчик начинается с 0.

| Итерация | `is_box_ahead()` | Выбранное действие |
| --- | --- | --- |
| 1 | `False` | `player.move_forward()` |
| 2 | `False` | `player.move_forward()` |
| 3 | `False` | `player.move_forward()` |
| 4 | `True` | `player.push()` |
| 5 | `True` | `player.push()` |
| 6 | `True` | `player.push()` |

В одном и том же цикле встречаются обе ветки: сначала герой идёт по свободным клеткам, затем толкает. Проверка выполняется заново на каждой итерации.

### Карта 8. Внутрь спирали

```text
>..B....
######.#
#.####B#
#F####.#
#.####.#
#B####.#
..B....#
######.#
```

**Учебная цель:** Сочетать повторяющиеся проходы и более короткие участки спирали.

**Задание:** Пройдите спираль: 6, 6, 5 и 3 клетки, повороты вправо. Повторяющуюся пару участков можно объединить внешним циклом.

**Подсказка:** У внутреннего прохода своя длина; не заходите в карман за монетой.

**Проверка тем же кодом:** поставьте первый ящик в `(1, 0)`, затем в отдельной копии в `(5, 0)`. Другие ящики оставьте на месте. Перед каждым запуском предскажите ветки.

**Разбор после предсказания:** фактическая трасса первого вызова внутреннего цикла (внешняя итерация `i = 0`) на основной расстановке. Итерации пронумерованы с 1; в `range` счётчик начинается с 0.

| Итерация | `is_box_ahead()` | Выбранное действие |
| --- | --- | --- |
| 1 | `False` | `player.move_forward()` |
| 2 | `False` | `player.move_forward()` |
| 3 | `True` | `player.push()` |
| 4 | `True` | `player.push()` |
| 5 | `True` | `player.push()` |
| 6 | `True` | `player.push()` |

В одном и том же цикле встречаются обе ветки: сначала герой идёт по свободным клеткам, затем толкает. Проверка выполняется заново на каждой итерации.

### Карта 9. Последний карман

```text
>.B.....
######.#
#.####.#
#.BF.#.#
#B####B#
#.####.#
...B...#
######.#
```

**Учебная цель:** Довести героя до внутренней монеты, сохраняя правило выбора действия.

**Задание:** Пройдите спираль: 6, 6, 5, 3 и 2 клетки, повороты вправо. Остановитесь, когда на монету встанет герой.

**Подсказка:** Ящик на монете ещё не означает победу.

**Проверка тем же кодом:** поставьте первый ящик в `(1, 0)`, затем в отдельной копии в `(5, 0)`. Другие ящики оставьте на месте. Перед каждым запуском предскажите ветки.

**Разбор после предсказания:** фактическая трасса первого вызова внутреннего цикла (внешняя итерация `i = 0`) на основной расстановке. Итерации пронумерованы с 1; в `range` счётчик начинается с 0.

| Итерация | `is_box_ahead()` | Выбранное действие |
| --- | --- | --- |
| 1 | `False` | `player.move_forward()` |
| 2 | `True` | `player.push()` |
| 3 | `True` | `player.push()` |
| 4 | `True` | `player.push()` |
| 5 | `True` | `player.push()` |
| 6 | `True` | `player.push()` |

В одном и том же цикле встречаются обе ветки: сначала герой идёт по свободным клеткам, затем толкает. Проверка выполняется заново на каждой итерации.

### Карта 10. Зеркальная спираль

```text
######.#
...B...#
#B####.#
#.####.#
#.BF.#.#
#.####B#
######.#
>...B...
```

**Учебная цель:** Перенести знакомый алгоритм на зеркальный маршрут с левыми поворотами.

**Задание:** Пройдите зеркальную спираль: 6, 6, 5, 3 и 2 клетки, повороты налево. Сохраните проверку внутри циклов.

**Подсказка:** Зеркало меняет повороты, а смысл проверки датчика остаётся прежним.

**Проверка тем же кодом:** поставьте первый ящик в `(1, 7)`, затем в отдельной копии в `(5, 7)`. Другие ящики оставьте на месте. Перед каждым запуском предскажите ветки.

**Разбор после предсказания:** фактическая трасса первого вызова внутреннего цикла (внешняя итерация `i = 0`) на основной расстановке. Итерации пронумерованы с 1; в `range` счётчик начинается с 0.

| Итерация | `is_box_ahead()` | Выбранное действие |
| --- | --- | --- |
| 1 | `False` | `player.move_forward()` |
| 2 | `False` | `player.move_forward()` |
| 3 | `False` | `player.move_forward()` |
| 4 | `True` | `player.push()` |
| 5 | `True` | `player.push()` |
| 6 | `True` | `player.push()` |

В одном и том же цикле встречаются обе ветки: сначала герой идёт по свободным клеткам, затем толкает. Проверка выполняется заново на каждой итерации.

## Преподавателю: решения и сравнение длины

Ниже приведены полные программы для основной расстановки. Условные программы
совпадают с решающей частью `demo/codomir/conditions/mapN.py` и проходят также
перечисленные варианты без изменения кода. Линейные решения относятся к основной
расстановке: после перестановки ящика их последовательность может стать неверной.

Длину считаем по непустым строкам учебной части: команда, заголовок `for`,
заголовок `if` и строка `else` дают по одной строке. Импорты, комментарии,
`set_map(...)` и `wait_quit()` не считаются. Каждый вызов записан на своей строке.
Это длина записи программы, а не число выполненных движений.

Кратчайшая линейная программа использует только команды, без условий и циклов;
её длина проверяется поиском кратчайшего пути в модели состояния.
Контрольная программа `for` без `if` тоже решает основную расстановку;
её минимальность среди всех программ с циклами не заявляется.

| Карта | Кратчайшее линейное | Условное | Контрольное `for` без `if` |
| --- | --- | --- | --- |
| 1 | 2 | 8 | — |
| 2 | 3 | 12 | — |
| 3 | 5 | 17 | — |
| 4 | 13 | 11 | 8 |
| 5 | 18 | 17 | 13 |
| 6 | 19 | 17 | 13 |
| 7 | 19 | 12 | 13 |
| 8 | 23 | 18 | 16 |
| 9 | 26 | 24 | 20 |
| 10 | 26 | 24 | 19 |

На картах 1–3 условия намеренно длиннее линейного решения: предмет изучения —
выбор и переносимость. На картах 4–10 условные решения короче **линейных**.
Это не означает, что они короче любой программы без `if`: например, на карте 4
контроль с `for` занимает 8 строк против 11 условных. Условия полезны тем,
что выбирают действие по фактическому расположению ящика; цикл повторяет эту проверку.

### Решения карты 1

**Условное: 8 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map1)

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

wait_quit()
```

**Кратчайшее линейное: 2 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map1)

player.push()
player.push()

wait_quit()
```

**Типичные ошибки:** Выполнить один толчок и считать, что ящик на монете уже дал победу; сделать обычный шаг сразу после толчка.

### Решения карты 2

**Условное: 12 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map2)

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

wait_quit()
```

**Кратчайшее линейное: 3 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map2)

player.move_forward()
player.push()
player.push()

wait_quit()
```

**Типичные ошибки:** Повторить первый результат `False` вместо новой проверки; после первого толчка попытаться пройти сквозь ящик.

### Решения карты 3

**Условное: 17 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map3)

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

player.turn_right()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

if player.is_box_ahead():
    player.push()
else:
    player.move_forward()

wait_quit()
```

**Кратчайшее линейное: 5 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map3)

player.push()
player.push()
player.turn_right()
player.push()
player.push()

wait_quit()
```

**Типичные ошибки:** Не повернуть на углу или считать, что датчик после поворота смотрит вправо; забыть повторно проверить ящик.

### Решения карты 4

**Условное: 11 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map4)

for i in range(6):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

player.turn_left()

for i in range(6):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

wait_quit()
```

**Кратчайшее линейное: 13 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map4)

player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.push()
player.turn_left()
player.move_forward()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()

wait_quit()
```

**Контроль с `for`, без `if`: 8 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map4)

player.move_forward()
for i in range(5):
    player.push()
player.turn_left()
for i in range(3):
    player.move_forward()
for i in range(3):
    player.push()

wait_quit()
```

**Типичные ошибки:** Отсчитывать толчки вместо продвижений героя; повернуть вправо вместо левого поворота.

### Решения карты 5

**Условное: 17 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map5)

for i in range(6):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

player.turn_right()

for i in range(5):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

player.turn_right()

for i in range(5):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

wait_quit()
```

**Кратчайшее линейное: 18 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map5)

player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.move_forward()
player.move_forward()
player.push()
player.push()

wait_quit()
```

**Контроль с `for`, без `if`: 13 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map5)

for i in range(2):
    player.move_forward()
for i in range(4):
    player.push()
player.turn_right()
player.move_forward()
for i in range(4):
    player.push()
player.turn_right()
for i in range(3):
    player.move_forward()
for i in range(2):
    player.push()

wait_quit()
```

**Типичные ошибки:** Сделать все три цикла одинаковой длины; забыть второй поворот.

### Решения карты 6

**Условное: 17 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map6)

for i in range(6):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

player.turn_right()

for i in range(6):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

player.turn_right()

for i in range(5):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

wait_quit()
```

**Кратчайшее линейное: 19 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map6)

player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()

wait_quit()
```

**Контроль с `for`, без `if`: 13 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map6)

player.move_forward()
for i in range(5):
    player.push()
player.turn_right()
for i in range(3):
    player.move_forward()
for i in range(3):
    player.push()
player.turn_right()
for i in range(2):
    player.move_forward()
for i in range(3):
    player.push()

wait_quit()
```

**Типичные ошибки:** Повторить длину первых проходов на последнем и уйти за монету.

### Решения карты 7

**Условное: 12 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map7)

for i in range(2):
    for j in range(6):
        if player.is_box_ahead():
            player.push()
        else:
            player.move_forward()
    player.turn_left()
for i in range(5):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

wait_quit()
```

**Кратчайшее линейное: 19 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map7)

player.move_forward()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.turn_left()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.turn_left()
player.move_forward()
player.push()
player.push()
player.push()
player.push()

wait_quit()
```

**Контроль с `for`, без `if`: 13 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map7)

for i in range(3):
    player.move_forward()
for i in range(3):
    player.push()
player.turn_left()
for i in range(2):
    player.move_forward()
for i in range(4):
    player.push()
player.turn_left()
player.move_forward()
for i in range(4):
    player.push()

wait_quit()
```

**Типичные ошибки:** Поставить поворот за внешним циклом: тогда он выполнится только один раз.

### Решения карты 8

**Условное: 18 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map8)

for i in range(2):
    for j in range(6):
        if player.is_box_ahead():
            player.push()
        else:
            player.move_forward()
    player.turn_right()
for i in range(5):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()
player.turn_right()
for i in range(3):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

wait_quit()
```

**Кратчайшее линейное: 23 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map8)

player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.turn_right()
player.push()
player.push()
player.push()

wait_quit()
```

**Контроль с `for`, без `if`: 16 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map8)

for i in range(2):
    player.move_forward()
for i in range(4):
    player.push()
player.turn_right()
player.move_forward()
for i in range(5):
    player.push()
player.turn_right()
for i in range(3):
    player.move_forward()
for i in range(2):
    player.push()
player.turn_right()
for i in range(3):
    player.push()

wait_quit()
```

**Типичные ошибки:** Использовать шесть повторений на коротких внутренних проходах; пропустить поворот после пяти шагов.

### Решения карты 9

**Условное: 24 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map9)

for i in range(2):
    for j in range(6):
        if player.is_box_ahead():
            player.push()
        else:
            player.move_forward()
    player.turn_right()
for i in range(5):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()
player.turn_right()
for i in range(3):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()
player.turn_right()
for i in range(2):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

wait_quit()
```

**Кратчайшее линейное: 26 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map9)

player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.turn_right()
player.move_forward()
player.push()
player.push()
player.turn_right()
player.push()
player.push()

wait_quit()
```

**Контроль с `for`, без `if`: 20 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map9)

player.move_forward()
for i in range(5):
    player.push()
player.turn_right()
for i in range(3):
    player.move_forward()
for i in range(3):
    player.push()
player.turn_right()
for i in range(2):
    player.move_forward()
for i in range(3):
    player.push()
player.turn_right()
player.move_forward()
for i in range(2):
    player.push()
player.turn_right()
for i in range(2):
    player.push()

wait_quit()
```

**Типичные ошибки:** Остановиться, когда ящик занял монету, или сделать лишний шаг после победы.

### Решения карты 10

**Условное: 24 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map10)

for i in range(2):
    for j in range(6):
        if player.is_box_ahead():
            player.push()
        else:
            player.move_forward()
    player.turn_left()
for i in range(5):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()
player.turn_left()
for i in range(3):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()
player.turn_left()
for i in range(2):
    if player.is_box_ahead():
        player.push()
    else:
        player.move_forward()

wait_quit()
```

**Кратчайшее линейное: 26 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map10)

player.move_forward()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.turn_left()
player.move_forward()
player.push()
player.push()
player.push()
player.push()
player.push()
player.turn_left()
player.move_forward()
player.move_forward()
player.push()
player.push()
player.push()
player.turn_left()
player.push()
player.push()
player.push()
player.turn_left()
player.push()
player.push()

wait_quit()
```

**Контроль с `for`, без `if`: 19 строк.**

```python
from codomir import player, set_map, wait_quit, maps

set_map(maps.conditions.map10)

for i in range(3):
    player.move_forward()
for i in range(3):
    player.push()
player.turn_left()
player.move_forward()
for i in range(5):
    player.push()
player.turn_left()
for i in range(2):
    player.move_forward()
for i in range(3):
    player.push()
player.turn_left()
for i in range(3):
    player.push()
player.turn_left()
for i in range(2):
    player.push()

wait_quit()
```

**Типичные ошибки:** Скопировать правые повороты карты 9; изменить правило выбора действия вместо направления маршрута.

## Запуск и проверка

Из корня репозитория с установленными зависимостями запустите демо, например в PowerShell:

```powershell
.venv/Scripts/python.exe demo/codomir/conditions/map1.py
.venv/Scripts/python.exe demo/codomir/conditions/map4.py
```

Замените номер на любой от 1 до 10. Окно остаётся открытым в `wait_quit()`;
закройте его перед следующим запуском. Для наблюдения игры нужен обычный видеодрайвер.

Автоматическая проверка без экрана (переменные задаются до импорта пакетов):

```powershell
$env:SDL_VIDEODRIVER = 'dummy'
$env:SDL_AUDIODRIVER = 'dummy'
New-Item -ItemType Directory -Force artifacts/conditions | Out-Null
.venv/Scripts/python.exe -m pytest tests/test_codomir_conditions.py tests/test_codomir_validator.py -p no:cacheprovider --basetemp=artifacts/conditions/lesson-check
```

`--basetemp` — отдельный временный каталог для pytest; не указывайте каталог с нужными файлами.
После проверки для видимых демо в той же PowerShell-сессии уберите dummy-драйверы:

```powershell
Remove-Item Env:SDL_VIDEODRIVER
Remove-Item Env:SDL_AUDIODRIVER
```

В Linux с существующей `.venv`:

```bash
source .venv/bin/activate
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m pytest tests/test_codomir_conditions.py tests/test_codomir_validator.py
```

Схемы, варианты и длины хранятся в
[`tests/fixtures/codomir_conditions.json`](../../tests/fixtures/codomir_conditions.json),
правила подсчёта — в [описании манифеста](../../tests/fixtures/codomir_conditions.md).
Исполняемые образцы находятся в [`demo/codomir/conditions/`](../../demo/codomir/conditions/).
Подробности проверки серии и её результаты — в [отчёте проверки](conditions-verification.md).
