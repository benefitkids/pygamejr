import pygamejr
import pygame

tilemap = pygamejr.TileMap('map/map.tmx')
background = tilemap.get_layer_sprites('background')
obstacles = tilemap.get_layer_sprites('obstacles')

player = tilemap.get_sprite_by_tileset_position(3, 12)
player.rect.centerx = 32
player.rect.centery = 4.5 * 64

foreground = tilemap.get_layer_sprites('foreground')

loot = tilemap.get_layer_sprites('loot')

for frame in pygamejr.every_frame(draw_sprites_rect=True):

    keys = pygame.key.get_pressed()

    rect = player.rect.copy()
    if keys[pygame.K_w]:
        player.rect.centery -= 1
    if keys[pygame.K_s]:
        player.rect.centery += 1
    if keys[pygame.K_d]:
        player.rect.centerx += 1
    if keys[pygame.K_a]:
        player.rect.centerx -= 1

    for sprite in obstacles:
        if player.rect.colliderect(sprite.rect):
            player.rect = rect
            break

    thing_for_delete = None
    for thing in loot:
        if player.rect.colliderect(thing.rect):
            thing_for_delete = thing

    if thing_for_delete:
        thing_for_delete.is_visible = False
        loot.remove(thing_for_delete)
