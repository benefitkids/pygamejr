import pygame
import pygamejr


class RotatingSquare(pygamejr.ImageSprite):
    def __init__(self, x, y):
        image = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.rect(image, "skyblue", (0, 0, 60, 60))
        super().__init__(image=image)
        self.rect.center = (x, y)
        self.speedX = 180
        self.speedY = 130
        self.rotation_speed = 90

    def update(self, dt=0):
        self.rotate(self.rotation_speed * dt)
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


square = RotatingSquare(200, 150)

for dt in pygamejr.every_frame():
    pass

pygame.quit()
