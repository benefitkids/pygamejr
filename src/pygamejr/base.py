import os
import pygame

pygame.init()

window_width = int(os.environ.get('PYGAMEJR_WINDOW_WIDTH') or 800)
window_height = int(os.environ.get('PYGAMEJR_WINDOW_HEIGHT') or 600)

screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)

clock = pygame.time.Clock()

_global_scene = None    # always rendered on top
_current_scene = None   # set by set_scene(), rendered below global


def get_global_scene():
    """Returns the global scene. Sprites added here are always visible regardless of current scene."""
    global _global_scene
    if _global_scene is None:
        from .scene import Scene
        _global_scene = Scene()
    return _global_scene


def get_current_scene():
    """Returns the current scene set by set_scene(), or None if not set."""
    return _current_scene


def set_scene(scene) -> None:
    global _current_scene
    _current_scene = scene


def next_frame():
    dt = clock.tick(60) / 1000
    screen.fill("black")
    if _current_scene is not None:
        _current_scene.update(dt)
        _current_scene.draw()
    global_scene = get_global_scene()
    global_scene.update(dt)
    global_scene.draw()
    pygame.display.flip()
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

        if _current_scene is not None:
            _current_scene.update(dt)
            _current_scene.draw(draw_rect=draw_sprites_rect)

        global_scene = get_global_scene()
        global_scene.update(dt)
        global_scene.draw(draw_rect=draw_sprites_rect)

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
