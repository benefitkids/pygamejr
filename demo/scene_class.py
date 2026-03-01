import pygame
import pygamejr

# =================================================================
# GLOBAL SCENE
# Sprites created here are visible in every scene.
# =================================================================

score = 0

player = pygamejr.ImageSprite(pygamejr.resources.image.player_ship1_orange)
player.rect.center = (400, 300)

hud_score = pygamejr.TextSprite("Score: 0", size=24)
hud_score.rect.topleft = (10, 10)

hud_level = pygamejr.TextSprite("Level 1", size=24)
hud_level.rect.topright = (790, 10)

hud_status = pygamejr.TextSprite("", size=48)
hud_status.rect.center = (400, 420)
hud_status.is_visible = False

# =================================================================
# SCENE CLASSES
# =================================================================

class MenuScene(pygamejr.Scene):
    def __init__(self):
        super().__init__()
        self._prev_space = False

        title1 = pygamejr.TextSprite("Space Shooter", size=56, scene=self)
        title1.rect.center = (400, 200)
        title2 = pygamejr.TextSprite("SPACE - start game", size=30, scene=self)
        title2.rect.center = (400, 320)

    def update(self, dt=0):
        super().update(dt)



class LevelScene(pygamejr.Scene):
    """Base class for game levels. Handles movement, coin collection and enemy collision."""
    SPEED = 250
    _COIN_POSITIONS = []

    def __init__(self, player):
        super().__init__()
        self.player = player
        self.state = None
        self._prev_esc = False
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()

    def _create_coins(self):
        for pos in self._COIN_POSITIONS:
            coin = pygamejr.ImageSprite(pygamejr.resources.image.coin_gold, scene=self)
            coin.rect.center = pos
            self.coins.add(coin)

    def init_scene(self):
        self.state = None
        for coin in list(self.coins):
            coin.kill()
        self.coins.empty()
        self._create_coins()
        return super().init_scene()

    def update(self, dt=0):
        global score
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

        if self.state or not self.player.is_visible:
            return

        # Coin collection
        collected = pygame.sprite.spritecollide(
            self.player, self.coins, True, pygame.sprite.collide_mask
        )
        if collected:
            score += 10 * len(collected)
            if not self.coins:
                self.state = "win"
                return

        # Enemy collision → game over
        if pygame.sprite.spritecollide(
            self.player, self.enemies, False, pygame.sprite.collide_mask
        ):
            self.state = "game_over"


class Level1Scene(LevelScene):
    _COIN_POSITIONS = [(200, 250), (560, 180), (400, 430)]

    def __init__(self, player):
        super().__init__(player)

        # Enemies (moving)
        self.bee1 = pygamejr.ImageSprite(pygamejr.resources.image.bee, scene=self)
        self.bee1.rect.center = (150, 150)
        self.bee2 = pygamejr.ImageSprite(pygamejr.resources.image.bee, scene=self)
        self.bee2.rect.center = (600, 220)
        self.enemies.add(self.bee1, self.bee2)

        title = pygamejr.TextSprite(
            "ARROWS - move   |   собери монетки!   |   ESC - меню",
            size=20,
            scene=self
        )
        title.rect.midbottom = (400, 590)

    def update(self, dt=0):
        super().update(dt)
        # Animate enemies
        self.bee1.rect.x += 120 * dt
        self.bee2.rect.x -= 90 * dt
        if self.bee1.rect.left > pygamejr.screen.get_width():
            self.bee1.rect.right = 0
        if self.bee2.rect.right < 0:
            self.bee2.rect.left = pygamejr.screen.get_width()

    def init_scene(self):
        self.bee1.rect.center = (150, 150)
        self.bee2.rect.center = (600, 220)
        return super().init_scene()


class Level2Scene(LevelScene):
    _COIN_POSITIONS = [(150, 350), (400, 200), (640, 420)]

    def __init__(self, player):
        super().__init__(player)

        # Enemies (moving)
        self.fly1 = pygamejr.ImageSprite(pygamejr.resources.image.fly, scene=self)
        self.fly1.rect.center = (180, 130)
        self.fly1_vel = [140, 110]
        self.fly2 = pygamejr.ImageSprite(pygamejr.resources.image.fly, scene=self)
        self.fly2.rect.center = (520, 340)
        self.fly2_vel = [-100, -80]
        self.enemies.add(self.fly1, self.fly2)

        title = pygamejr.TextSprite(
            "ARROWS - move   |   собери монетки!   |   ESC - меню",
            size=20,
            scene=self,
        )
        title.rect.midbottom = (400, 590)

    def update(self, dt=0):
        super().update(dt)
        screen_rect = pygamejr.screen.get_rect()
        # Animate enemies with bounce
        for fly, vel in [(self.fly1, self.fly1_vel), (self.fly2, self.fly2_vel)]:
            fly.rect.x += vel[0] * dt
            fly.rect.y += vel[1] * dt
            if fly.rect.left < screen_rect.left or fly.rect.right > screen_rect.right:
                vel[0] *= -1
                fly.rect.clamp_ip(screen_rect)
            if fly.rect.top < screen_rect.top or fly.rect.bottom > screen_rect.bottom:
                vel[1] *= -1
                fly.rect.clamp_ip(screen_rect)

    def init_scene(self):
        self.fly1.rect.center = (180, 130)
        self.fly1_vel = [140, 110]
        self.fly2.rect.center = (520, 340)
        self.fly2_vel = [-100, -80]
        return super().init_scene()

# =================================================================
# CREATE SCENES
# =================================================================

menu_scene   = MenuScene()
level1_scene = Level1Scene(player)
level2_scene = Level2Scene(player)

# =================================================================
# START — player and HUD hidden until game begins
# =================================================================

pygamejr.set_scene(menu_scene)
player.is_visible    = False
hud_score.is_visible = False
hud_level.is_visible = False

for dt in pygamejr.every_frame():

    hud_score.text = f"Score: {score}"
    keys = pygame.key.get_pressed()

    current_scene = pygamejr.get_current_scene()

    if current_scene == menu_scene:
        if keys[pygame.K_SPACE]:
            pygamejr.set_scene(level1_scene)
            player.is_visible = True
            hud_score.is_visible = True
            hud_level.is_visible = True
            hud_status.is_visible = False
    elif current_scene in [level1_scene, level2_scene]:
        if keys[pygame.K_ESCAPE]:
            pygamejr.set_scene()
        if current_scene.state == 'win':
            if current_scene == level1_scene:
                pygamejr.set_scene(level2_scene)
                hud_level.text = 'Level 2'
            elif current_scene == level2_scene:
                player.is_visible = False
                hud_score.is_visible = False
                hud_level.is_visible = False
                hud_status.text = f"YOU WIN! {score} pts"
                hud_status.is_visible = True
                pygamejr.set_scene(None)
                pygamejr.set_scene(menu_scene)
        elif current_scene.state == 'game_over':
            hud_status.text = "GAME OVER"
            hud_status.is_visible = True
            player.is_visible = False
            pygamejr.set_scene(menu_scene)
