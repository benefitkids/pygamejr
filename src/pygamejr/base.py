import os
import pygame

pygame.init()

window_width = int(os.environ.get('PYGAMEJR_WINDOW_WIDTH') or 800)
window_height = int(os.environ.get('PYGAMEJR_WINDOW_HEIGHT') or 600)

screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)

clock = pygame.time.Clock()

_current_scene = None

def get_current_scene():
    global _current_scene
    if _current_scene is None:
        from .scene import Scene
        _current_scene = Scene()
    return _current_scene

def set_scene(scene) -> None:
    global _current_scene
    _current_scene = scene

def next_frame():
    scene = get_current_scene()
    screen.fill("black")
    scene.update()
    scene.draw()
    pygame.display.flip()
    clock.tick(60)
    return not is_quit()

def every_frame(frame_count=0, draw_sprites_rect=False):
    running = True
    frame = -1
    while running:
        dt = clock.tick(60) / 1000

        if is_quit() or frame >= frame_count:
            break

        if frame_count:
            frame += 1

        screen.fill("black")

        yield dt

        scene = get_current_scene()
        scene.update()
        scene.draw(draw_rect=draw_sprites_rect)

        pygame.display.flip()

_is_quit = False

def is_quit():
    global _is_quit

    if _is_quit:
        return True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            _is_quit = True
            return True
    return False


def wait_quit():
    for _ in every_frame():
        pass
