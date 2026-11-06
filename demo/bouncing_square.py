import pygame
import pygamejr


class Square(pygamejr.BaseSprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.FRect(0, 0, 60, 60)
        self.rect.center = (x, y)
        self.color = "skyblue"
        self.speedX = 180
        self.speedY = 130

    def update(self, dt=0):
        self.rect.x += self.speedX * dt
        self.rect.y += self.speedY * dt
        width, height = pygamejr.screen.get_size()

        if self.rect.left <= 0:
            self.rect.left = 0
            if self.speedX < 0:
                self.speedX = -self.speedX
        elif self.rect.right >= width:
            self.rect.right = width
            if self.speedX > 0:
                self.speedX = -self.speedX

        if self.rect.top <= 0:
            self.rect.top = 0
            if self.speedY < 0:
                self.speedY = -self.speedY
        elif self.rect.bottom >= height:
            self.rect.bottom = height
            if self.speedY > 0:
                self.speedY = -self.speedY

    def draw(self, draw_rect=False):
        if not self.is_visible:
            return
        pygame.draw.rect(pygamejr.screen, self.color, self.rect)
        if draw_rect:
            pygame.draw.rect(pygamejr.screen, "red", self.rect, 1)


square = Square(200, 150)

for dt in pygamejr.every_frame():
    pass

pygame.quit()
