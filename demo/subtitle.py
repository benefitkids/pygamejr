import pygamejr

STATE_GAME = 'game'
STATE_GAME_OVER = 'game_over'

text = pygamejr.SubtitlesSprite(['3', '2', '1', "Hello World!"], 48)
text.rect.center = (400, 300)
text.is_visible = True

game_over_text = pygamejr.TextSprite('Game Over!', 48)
game_over_text.rect.center = (400, 300)
game_over_text.is_visible = False

state = STATE_GAME

for dt in pygamejr.every_frame():
    if state == STATE_GAME:
        text.update()
        text.rect.center = (400, 300)
        if not text.is_visible:
            state = 'game_over'
            game_over_text.is_visible = True
    elif state == STATE_GAME_OVER:
        game_over_text.rect.centerx += 1
