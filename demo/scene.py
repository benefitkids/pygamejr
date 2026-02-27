import pygame
import pygamejr

# =================================================================
# GLOBAL SCENE
#
# Sprites created before the first set_scene call are placed
# in the global scene and drawn ON TOP of any current scene.
# Player and HUD live here — they are visible across all levels.
# =================================================================

player = pygamejr.ImageSprite(pygamejr.resources.image.player_ship1_orange)
player.rect.center = (400, 500)

hud_score = pygamejr.TextSprite("Score: 0", size=24)
hud_score.rect.topleft = (10, 10)

hud_level = pygamejr.TextSprite("Level 1", size=24)
hud_level.rect.topright = (790, 10)

score = 0

# =================================================================
# MENU SCENE
# =================================================================
menu_scene = pygamejr.Scene()
pygamejr.set_scene(menu_scene)

pygamejr.TextSprite("Space Shooter", size=56).rect.center = (400, 200)
pygamejr.TextSprite("SPACE - start game", size=30).rect.center = (400, 320)

# =================================================================
# LEVEL 1 — bees and ladybugs
# =================================================================
level1_scene = pygamejr.Scene()
pygamejr.set_scene(level1_scene)

bee1 = pygamejr.ImageSprite(pygamejr.resources.image.bee)
bee1.rect.center = (150, 150)

bee2 = pygamejr.ImageSprite(pygamejr.resources.image.bee)
bee2.rect.center = (500, 100)

pygamejr.ImageSprite(pygamejr.resources.image.ladybug).rect.center = (650, 200)

pygamejr.TextSprite(
    "ARROWS - move   |   N - next level   |   ESC - menu",
    size=20
).rect.midbottom = (400, 590)

# =================================================================
# LEVEL 2 — flies and frogs
# =================================================================
level2_scene = pygamejr.Scene()
pygamejr.set_scene(level2_scene)

fly1 = pygamejr.ImageSprite(pygamejr.resources.image.fly)
fly1.rect.center = (180, 130)

fly2 = pygamejr.ImageSprite(pygamejr.resources.image.fly)
fly2.rect.center = (520, 160)

pygamejr.ImageSprite(pygamejr.resources.image.frog).rect.center = (340, 80)
pygamejr.ImageSprite(pygamejr.resources.image.worm_green).rect.center = (650, 200)

pygamejr.TextSprite(
    "ARROWS - move   |   P - previous level   |   ESC - menu",
    size=20
).rect.midbottom = (400, 590)

# =================================================================
# Start from the menu.
# Player and HUD are hidden — not needed on the menu screen.
# =================================================================
pygamejr.set_scene(menu_scene)
player.is_visible = False
hud_score.is_visible = False
hud_level.is_visible = False

SPEED = 250
prev_space = prev_n = prev_p = prev_esc = False

for dt in pygamejr.every_frame():
    keys = pygame.key.get_pressed()
    current = pygamejr.get_current_scene()

    # --- Menu ---
    if current is menu_scene:
        if keys[pygame.K_SPACE] and not prev_space:
            player.rect.center = (400, 500)
            player.is_visible = True
            hud_score.is_visible = True
            hud_level.is_visible = True
            hud_level.text = "Level 1"
            pygamejr.set_scene(level1_scene)

    # --- Game levels ---
    else:
        # Player movement works on any level because
        # player lives in the global scene.
        if keys[pygame.K_LEFT]:
            player.rect.x -= SPEED * dt
        if keys[pygame.K_RIGHT]:
            player.rect.x += SPEED * dt
        if keys[pygame.K_UP]:
            player.rect.y -= SPEED * dt
        if keys[pygame.K_DOWN]:
            player.rect.y += SPEED * dt
        player.rect.clamp_ip(pygamejr.screen.get_rect())

        # Animate level 1 enemies
        if current is level1_scene:
            bee1.rect.x += 120 * dt
            bee2.rect.x -= 90 * dt
            if bee1.rect.left > pygamejr.screen.get_width():
                bee1.rect.right = 0
            if bee2.rect.right < 0:
                bee2.rect.left = pygamejr.screen.get_width()

        # Animate level 2 enemies
        if current is level2_scene:
            fly1.rect.x += 140 * dt
            fly2.rect.x -= 100 * dt
            if fly1.rect.left > pygamejr.screen.get_width():
                fly1.rect.right = 0
            if fly2.rect.right < 0:
                fly2.rect.left = pygamejr.screen.get_width()

        # Level 1 -> Level 2
        # Player position is preserved automatically on transition!
        if current is level1_scene and keys[pygame.K_n] and not prev_n:
            score += 100
            hud_score.text = f"Score: {score}"
            hud_level.text = "Level 2"
            pygamejr.set_scene(level2_scene)

        # Level 2 -> Level 1
        if current is level2_scene and keys[pygame.K_p] and not prev_p:
            score += 100
            hud_score.text = f"Score: {score}"
            hud_level.text = "Level 1"
            pygamejr.set_scene(level1_scene)

        # Return to menu
        if keys[pygame.K_ESCAPE] and not prev_esc:
            player.is_visible = False
            hud_score.is_visible = False
            hud_level.is_visible = False
            pygamejr.set_scene(menu_scene)

    prev_space = keys[pygame.K_SPACE]
    prev_n = keys[pygame.K_n]
    prev_p = keys[pygame.K_p]
    prev_esc = keys[pygame.K_ESCAPE]
