import pygame

# инициализация должна быть на прикладном уровне
screen =  pygame.display.set_mode((800, 600), pygame.RESIZABLE)

clock = pygame.time.Clock()

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
    running = False
    while running:
        if is_quit():
            running = False