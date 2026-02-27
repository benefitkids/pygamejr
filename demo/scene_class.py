import pygame
import pygamejr

# =================================================================
# GLOBAL SCENE
# Sprites created here are visible in every scene.
# =================================================================

player = pygamejr.ImageSprite(pygamejr.resources.image.player_ship1_orange)
player.rect.center = (400, 500)

hud_score = pygamejr.TextSprite("Score: 0", size=24)
hud_score.rect.topleft = (10, 10)

hud_level = pygamejr.TextSprite("Level 1", size=24)
hud_level.rect.topright = (790, 10)

# =================================================================
# SCENE CLASSES
# =================================================================

class MenuScene(pygamejr.Scene):
    def __init__(self, player, hud_score, hud_level):
        super().__init__()
        self.player = player
        self.hud_score = hud_score
        self.hud_level = hud_level
        self.next_scene = None  # wired up after level scenes are created
        self._prev_space = False

        previous = pygamejr.get_current_scene()
        pygamejr.set_scene(self)
        pygamejr.TextSprite("Space Shooter", size=56).rect.center = (400, 200)
        pygamejr.TextSprite("SPACE - start game", size=30).rect.center = (400, 320)
        pygamejr.set_scene(previous)

    def update(self, dt=0):
        super().update(dt)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not self._prev_space and self.next_scene:
            self.player.rect.center = (400, 500)
            self.player.is_visible = True
            self.hud_score.is_visible = True
            self.hud_level.is_visible = True
            self.hud_level.text = "Level 1"
            pygamejr.set_scene(self.next_scene)
        self._prev_space = keys[pygame.K_SPACE]


class LevelScene(pygamejr.Scene):
    """Base class for game levels. Handles player movement and ESC -> menu."""
    SPEED = 250

    def __init__(self, player, hud_score, hud_level, score_ref):
        super().__init__()
        self.player = player
        self.hud_score = hud_score
        self.hud_level = hud_level
        self.score_ref = score_ref
        self.menu_scene = None  # wired up after all scenes are created
        self._prev_esc = False

    def update(self, dt=0):
        super().update(dt)
        keys = pygame.key.get_pressed()
        p = self.player
        if keys[pygame.K_LEFT]:
            p.rect.x -= self.SPEED * dt
        if keys[pygame.K_RIGHT]:
            p.rect.x += self.SPEED * dt
        if keys[pygame.K_UP]:
            p.rect.y -= self.SPEED * dt
        if keys[pygame.K_DOWN]:
            p.rect.y += self.SPEED * dt
        p.rect.clamp_ip(pygamejr.screen.get_rect())

        if keys[pygame.K_ESCAPE] and not self._prev_esc:
            self.player.is_visible = False
            self.hud_score.is_visible = False
            self.hud_level.is_visible = False
            pygamejr.set_scene(self.menu_scene)
        self._prev_esc = keys[pygame.K_ESCAPE]


class Level1Scene(LevelScene):
    def __init__(self, player, hud_score, hud_level, score_ref):
        super().__init__(player, hud_score, hud_level, score_ref)
        self.next_scene = None  # wired up after level2_scene is created
        self._prev_n = False

        previous = pygamejr.get_current_scene()
        pygamejr.set_scene(self)
        self.bee1 = pygamejr.ImageSprite(pygamejr.resources.image.bee)
        self.bee1.rect.center = (150, 150)
        self.bee2 = pygamejr.ImageSprite(pygamejr.resources.image.bee)
        self.bee2.rect.center = (500, 100)
        pygamejr.ImageSprite(pygamejr.resources.image.ladybug).rect.center = (650, 200)
        pygamejr.TextSprite(
            "ARROWS - move   |   N - next level   |   ESC - menu",
            size=20
        ).rect.midbottom = (400, 590)
        pygamejr.set_scene(previous)

    def update(self, dt=0):
        super().update(dt)  # player movement + ESC
        # Animate bees
        self.bee1.rect.x += 120 * dt
        self.bee2.rect.x -= 90 * dt
        if self.bee1.rect.left > pygamejr.screen.get_width():
            self.bee1.rect.right = 0
        if self.bee2.rect.right < 0:
            self.bee2.rect.left = pygamejr.screen.get_width()
        # N -> next level
        keys = pygame.key.get_pressed()
        if keys[pygame.K_n] and not self._prev_n and self.next_scene:
            self.score_ref[0] += 100
            self.hud_score.text = f"Score: {self.score_ref[0]}"
            self.hud_level.text = "Level 2"
            pygamejr.set_scene(self.next_scene)
        self._prev_n = keys[pygame.K_n]


class Level2Scene(LevelScene):
    def __init__(self, player, hud_score, hud_level, score_ref):
        super().__init__(player, hud_score, hud_level, score_ref)
        self.prev_scene = None  # wired up after level1_scene is created
        self._prev_p = False

        previous = pygamejr.get_current_scene()
        pygamejr.set_scene(self)
        self.fly1 = pygamejr.ImageSprite(pygamejr.resources.image.fly)
        self.fly1.rect.center = (180, 130)
        self.fly2 = pygamejr.ImageSprite(pygamejr.resources.image.fly)
        self.fly2.rect.center = (520, 160)
        pygamejr.ImageSprite(pygamejr.resources.image.frog).rect.center = (340, 80)
        pygamejr.ImageSprite(pygamejr.resources.image.worm_green).rect.center = (650, 200)
        pygamejr.TextSprite(
            "ARROWS - move   |   P - previous level   |   ESC - menu",
            size=20
        ).rect.midbottom = (400, 590)
        pygamejr.set_scene(previous)

    def update(self, dt=0):
        super().update(dt)  # player movement + ESC
        # Animate flies
        self.fly1.rect.x += 140 * dt
        self.fly2.rect.x -= 100 * dt
        if self.fly1.rect.left > pygamejr.screen.get_width():
            self.fly1.rect.right = 0
        if self.fly2.rect.right < 0:
            self.fly2.rect.left = pygamejr.screen.get_width()
        # P -> previous level
        keys = pygame.key.get_pressed()
        if keys[pygame.K_p] and not self._prev_p and self.prev_scene:
            self.score_ref[0] += 100
            self.hud_score.text = f"Score: {self.score_ref[0]}"
            self.hud_level.text = "Level 1"
            pygamejr.set_scene(self.prev_scene)
        self._prev_p = keys[pygame.K_p]


# =================================================================
# CREATE AND WIRE UP SCENES
# =================================================================

score_ref = [0]

menu_scene   = MenuScene(player, hud_score, hud_level)
level1_scene = Level1Scene(player, hud_score, hud_level, score_ref)
level2_scene = Level2Scene(player, hud_score, hud_level, score_ref)

menu_scene.next_scene    = level1_scene
level1_scene.next_scene  = level2_scene
level1_scene.menu_scene  = menu_scene
level2_scene.prev_scene  = level1_scene
level2_scene.menu_scene  = menu_scene

# =================================================================
# START — player and HUD hidden until game begins
# =================================================================

pygamejr.set_scene(menu_scene)
player.is_visible    = False
hud_score.is_visible = False
hud_level.is_visible = False

for dt in pygamejr.every_frame():
    pass
