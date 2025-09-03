import os
import pygame

pygame.init()

window_width = int(os.environ.get('PYGAMEJR_WINDOW_WIDTH') or 800)
window_height = int(os.environ.get('PYGAMEJR_WINDOW_HEIGHT') or 600)

screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)

clock = pygame.time.Clock()

def next_frame():
    pygame.display.flip()
    clock.tick(60) / 1000
    screen.fill("black")
    return not is_quit()

def every_frame(frame_count=0):
    running = True
    frame = -1
    while running:
        dt = clock.tick(60) / 1000

        if is_quit() or frame >= frame_count :
            break

        if frame_count:
            frame += 1

        screen.fill("black")
        yield dt
        pygame.display.flip()


def is_quit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
    return False


def wait_quit():
    running = True
    while running:
        if is_quit():
            running = False