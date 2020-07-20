import pygame, sys, os
from random import choice
from pygame.locals import *


pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption('Pygame Platformer')
WINDOW_SIZE = (600,800)
screen = pygame.display.set_mode(WINDOW_SIZE,0,32) 
display = pygame.Surface((300, 400))

moving_right = False
moving_left = False
vertical_momentum = 0
air_timer = 0

true_scroll = [0,0]

def load_map():
    
    d = [
        "1100",
        "0101"
        "0101",
        "0110",
        "0101",
        "0001",
        "1101",
        "0001",
        "1110",
        "0100"
        "1101",
        "0110",
        "0000",
        "0000",
        "0000",
        "1101",
        "0000",
        "1101"]
    data = [choice(d) + choice(d) + choice(d) for x in range(30)]
    data.append("11111111111111111111")
    return data


global animation_frames
animation_frames = {}

def load_animation(path,frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        # player_animations/idle/idle_0.png
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((255,255,255))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

def change_action(action_var,frame,new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var,frame
        

animation_database = {}

animation_database['run'] = load_animation('player_animations/run',[7,7])
animation_database['idle'] = load_animation('player_animations/idle',[7,7,40])

game_map = load_map()

grass_img = pygame.image.load('grass.png')
dirt_img = pygame.image.load('dirt.png')

player_action = 'idle'
player_frame = 0
player_flip = False

player_rect = pygame.Rect(100,100,5,13)

background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]

def collision_test(rect,tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect,movement,tiles):
    collision_types = {'top':False,'bottom':False,'right':False,'left':False}
    rect.x += movement[0]
    hit_list = collision_test(rect,tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect,tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types


def show(dsp, srf, x, y):
    dsp.blit(srf, (x * 16 - scroll[0], y * 16 - scroll[1]))


def tilerects():
    tile_rects = []
    y = 0
    for layer in game_map:
        x = 0
        for tile in layer:
            if tile == '1':
                show(display, dirt_img, x, y)
                # show(display2, tile_cover, x + 1, y)
                tile_rects.append(pygame.Rect(x * 16, y * 16,16,16))
            x += 1
        y += 1
    return tile_rects


# player_cover = pygame.Surface((5, 13))
# player_cover.fill((0, 0, 0))
# tile_cover = pygame.Surface((32, 32))
# tile_cover.fill((0, 0, 255))


#
#                             THE LOOP
#

mount = pygame.image.load("mountains.png")
sea = pygame.image.load("sea.png")
while True: # game loop
    display.fill((146,244,255)) # clear screen by filling it with blue

    # screen.blit(pygame.transform.scale(display2, WINDOW_SIZE), (0,0))
    true_scroll[0] += (player_rect.x-true_scroll[0]-152)/20
    true_scroll[1] += (player_rect.y-true_scroll[1]-106)/20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    #                ---   parallax  ---

    # pygame.draw.rect(display, (7, 80, 75), pygame.Rect(0, 120, 300, 400))


    #                 --------- BACKGROUND --------

    display.blits(blit_sequence=(
        (mount, (0, 0)),
        (sea, (0, 120))))
    # for background_object in background_objects:
    #     obj_rect = pygame.Rect(
    #         background_object[1][0] - scroll[0] * background_object[0],
    #         background_object[1][1] - scroll[1] * background_object[0],
    #         background_object[1][2],
    #         background_object[1][3])
        
    #     if background_object[0] == 0.5:
    #         pygame.draw.rect(display, (14, 222, 150), obj_rect)
        
    #     else:
    #         pygame.draw.rect(display, (9, 91, 85), obj_rect)

    tile_rects = tilerects()

    player_movement = [0,0]
    if moving_right == True:
        player_movement[0] += 2
    if moving_left == True:
        player_movement[0] -= 2
    player_movement[1] += vertical_momentum
    vertical_momentum += 0.2
    if vertical_momentum > 3:
        vertical_momentum = 3

    if player_movement[0] == 0:
        player_action,player_frame = change_action(player_action,player_frame,'idle')
    if player_movement[0] > 0:
        player_flip = False
        player_action,player_frame = change_action(player_action,player_frame,'run')
    if player_movement[0] < 0:
        player_flip = True
        player_action,player_frame = change_action(player_action,player_frame,'run')

    player_rect, collisions = move(player_rect,player_movement,tile_rects)

    if collisions['bottom'] == True:
        air_timer = 0
        vertical_momentum = 0
    else:
        air_timer += 1

    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_img = animation_frames[player_img_id]

    # display the player not vertically
    # what has scroll... to do with the scroll
    # display.blit(
    #     player_cover,
    #     (player_rect.x - scroll[0], player_rect.y - scroll[1]))
    display.blit(
        pygame.transform.flip(player_img,player_flip, False),
        (player_rect.x - scroll[0], player_rect.y - scroll[1]))


    for event in pygame.event.get(): # event loop
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                display.fill((0, 0, 0))
                player_rect.x = 100
                player_rect.y = 100
                game_map = load_map()
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP:
                if air_timer < 6:
                    vertical_momentum = -5
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False
        
    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0,0))
    pygame.display.update()
    clock.tick(60)
