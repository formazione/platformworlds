import pygame, sys, os
from random import choice, randrange
from pygame.locals import *




def load_map() -> list:
    ''' Map 30 rows x 300 columns generated randomly '''
    # It's called by game_map and is used to blit the map in tilerects()
    data = [] # will contain the rows with 0 and 1 generate randomly
    line = "" # create a "101010101010" random string with 0 and 1 to append to data
    data.append("1"*300)
    brother_put = 0
    for row in range(30): # 30 rows of 0 and 1
        line += "1"
        for col in range(300): # 30 1 and 0 for line
            # I made more 0es to have less chance to have a close path
            line += choice(["0", "0", "0", "1"])
        line += "1"
        data.append(line) # add the random line
        line = "" # empty the line for the next row

    data.append("1"*300)
    x = randrange(150, 295)
    y = randrange(3, 28)
    data[y] = list(data[y])
    data[y][x] = "3"
    data[y] = "".join(data[y])
    print(f"my brother is at height:{y} width{x}")
    return data


def tilerects():

    def show(dsp, srf, x, y):
        # the tiles are 16 pixel each, so to convert the position in the list
        # in the pixel on the scrreen just multiply per 16.
        # scroll[0] is increased when the user goes right the tiles are 
        # shifted on the left (same when goes down the tiles shift up)
        dsp.blit(srf, (x * 16 - scroll[0], y * 16 - scroll[1]))
    
    tile_rects = [] # this will contain the tiles position
    y = 0
    for layer in game_map: # iteration of 0 and 1... space or tile
        x = 0
        for tile in layer:
            
            right = x*16 < player_rect.x + 200 and y*16 < player_rect.y + 200
            if right:
                if tile == '1': # diplay a tile (eventually shifted with scroll[0])
                    show(display, dirt_img, x, y)
                    # show(display2, tile_cover, x + 1, y)
                    # the tile_rects contains the rectangle useful for collision detection
                    tile_rects.append(pygame.Rect(x * 16, y * 16,16,16))
                if tile == '3':
                    show(display, brother, x, y)
                    # tile_rects.append(pygame.Rect(x * 16, y * 16,16,16))
                x += 1 # counter for the index in the list of 0 and 1 (game_map)
        y += 1
    return tile_rects



def load_animation(path,frame_durations):
    ''' Example:
    animation_database = {} #                        path        frame_durations
    animation_database['run'] = load_animation('player_animations/run',[7,7])
    '''
    animation_name = path.split('/')[-1] # it's "run" in the example above
    animation_frame_data = [] # will contain run_0, run_1 i.e. animation_frame_id
    n = 0
    for frame in frame_durations: # frame_durations = [7,7]
        # the following string goes into animation_frame_data
        animation_frame_id = animation_name + '_' + str(n) # run_0 ... 
        img_loc = path + '/' + animation_frame_id + '.png' # path = player_animations/run
        # img_loc = player_animations/run/run:0.png ... in the example
        # player_animations/idle/idle_0.png
        animation_image = pygame.image.load(img_loc).convert() # this is good for frame rate
        animation_image.set_colorkey((255,255,255)) # the color white becomes transparent
        # animation_frames is a dictionary
        # animation_frames["run_0"]
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            # this will add 7 times run_0 and 7 times run_1
            # this will hold all the name of the frames of the action run in animation_database["run"]
            # for every frame it will show run_0 run_0.... run_1.... so that it last for 7 frames
            animation_frame_data.append(animation_frame_id) # = "run_0"
        n += 1
    return animation_frame_data

def change_action(action_var,frame,new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var,frame
        


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


# Let's start here with some initialization stuff

pygame.init() # all starts here
pygame.mixer.init()
pygame.mixer.music.load("001.mp3")
pygame.mixer.music.play()
clock = pygame.time.Clock() # for the frame rate (not to go too fast)
pygame.display.set_caption('Pygame Platformer')
WINDOW_SIZE = (1200,800)
screen = pygame.display.set_mode(WINDOW_SIZE,0,32)  # Main surface
display = pygame.Surface((600, 400)) # temporary surface to scale on screen
moving_right = False # where is moving
moving_left = False
vertical_momentum = 0 # for the jump
air_timer = 0 # how long the jump is ?

true_scroll = [0,0] # the camera control
game_map = load_map() # 0 and 1... and other numbers for tile
# global animation_frames
# this will have for "run" the img repeated for 7 times each, so that does not go too fast
animation_frames = {} # key = frame name, value = run_0, run_0, ... run_1...
animation_database = {} # database with a key for each action (run and idle)
# the value are the name of the images: run_0, run_1
'''
{"run" : ["run_0", "run_1"]}

'''
animation_database['run'] = load_animation('player_animations/run',[7,7])
# the duration of each frame is different here
animation_database['idle'] = load_animation('player_animations/idle',[7,7,40])
grass_img = pygame.image.load('grass.png').convert()
dirt_img = pygame.image.load('dirt.png').convert()
brother = pygame.image.load('brother.png').convert()
# brother.set_colorkey((255,255,255))
player_action = 'idle'
player_frame = 0
player_flip = False
# starting position
player_rect = pygame.Rect(100, 100, 5, 13)
# some object in background, for the moment I do not show them
# background_objects = [
#     [0.25,[120,10,70,400]],
#     [0.25,[280,30,40,400]],
#     [0.5,[30,40,40,400]],
#     [0.5,[130,90,100,400]],
#     [0.5,[300,80,120,400]]]



# This surfaces are used to cover the images and save frames?
# player_cover = pygame.Surface((5, 13))
# player_cover.fill((0, 0, 0))

# tile_cover = pygame.Surface((32, 32))
# tile_cover.fill((0, 0, 255))


#
#                             THE LOOP
#

# mount = pygame.image.load("mountains.png")
# sea = pygame.image.load("sea.png")
while True: # game loop
    display.fill((0,0,0)) # clear screen by filling it with blue

    # screen.blit(pygame.transform.scale(display2, WINDOW_SIZE), (0,0))
    true_scroll[0] += (player_rect.x-true_scroll[0]-152)/20
    true_scroll[1] += (player_rect.y-true_scroll[1]-106)/20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    #                ---   parallax  ---

    # pygame.draw.rect(display, (7, 80, 75), pygame.Rect(0, 120, 300, 400))


    #                 --------- BACKGROUND  OBJECTS --------

    # display.blits(blit_sequence=(
    #     (mount, (0, 0)),
    #     # (sea, (0, 120))
    #     ))
    # for background_object in background_objects:
    #     obj_rect = pygame.Rect(
    #         background_object[1][0] - scroll[0] * background_object[0],
    #         background_object[1][1] - scroll[1] * background_object[0],
    #         background_object[1][2],
    #         background_object[1][3])
    #     # THIS IS GREEN
    #     if background_object[0] == 0.5:
    #         pygame.draw.rect(display, (14, 222, 250), obj_rect)
    #         # display.blit(sea, obj_rect)
    #     # THIS IS BLUE
    #     else:
    #         pygame.draw.rect(display, (9, 91, 185), obj_rect)

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
    # the list of animation_frames["run"] is made in load_images
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
                # display.fill((0, 0, 0))
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
