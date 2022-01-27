import pygame, sys, os
from random import choice, randrange
from pygame.locals import *
import math

def load_animation(path: str, frame_durations: list):
    ''' Example:
    animation_database = {} #                        path        frame_durations
    animation_database['run'] = load_animation('player_animations/run',[7,7])
    frame_durations = [7,7] number of frames that are repeated for 7 times each
    '''
    animation_name = path.split('/')[-1] # filename of png
    animation_frame_data = [] # list of frames filenames
    n = 0 # counter of frames for run, idle ... frames
    for frame in frame_durations: # frame_durations = [7,7]
        # 
        animation_frame_id = animation_name + '_' + str(n) # run_0 ... 
        img_loc = path + '/' + animation_frame_id + '.png' # path = player_animations/run
        animation_image = pygame.image.load(img_loc).convert() # this is good for frame rate
        animation_image.set_colorkey((255,255,255)) # the color white becomes transparent
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id) # = "run_0"
        n += 1
    return animation_frame_data

fps_list = []
def show_fps():
    ''' shows the frame rate on the screen '''
    fps = f"Fps: {int(clock.get_fps())} {score=}" # get the clocl'fps
    fps_media = fps_font.render(fps, 1, pygame.Color("white"))
    display.blit(fps_media, (0, 0))


def create_map() -> list:
    ''' Map 30 rows x 300 columns generated randomly '''

    data = [] # will contain the rows with 0 and 1 generate randomly
    def generate_map_filled():
        for row in range(10):
            # ten levels with platforms
            data.append([choice([0,0,0,0,0,0,0,0,0,0,0,6,7]) for x in range(300)])
        # some stones and trees in the row above the path
        data.append([choice([0,0,0,0,0,1,2,5]) for x in range(300)])
        # The ground
        data.append([4 for x in range(300)])

    def generate_path():
        percorso = [] # used to place the brothen on the path
        col = 10 # row
        row = 10
        mem = 0
        while col < 299: # until end of 300 col
            # data[x][d] = 0
            digr = choice([0,1,2])
            if digr == 0 and mem !=2: # goes up
                if row > 1:
                    row -=1 
            if digr == 1: # goes right
                col += 1
            if digr == 2 and mem != 0: # goes down
                if row < 4:
                    row += 1
            mem = digr

            data[row][col] = 0
            percorso.append([row, col])
        return percorso

    def player_space():
        data[10][10] = 0
        data[10][11] = 0

    def coin_place(percorso):
        for i in range(50):
            x, y = choice(percorso)
            data[x][y] = 2
    
    def brother_place(percorso):
        # data[y] = list(data[y])
        x, y = choice(percorso)
        data[x][y] = 3
        # data[y] = "".join(data[y])
        print(f"my brother is at height:{y} width{x}")

    # map algorhithm
    generate_map_filled()
    percorso = generate_path()
    player_space()
    coin_place(percorso)
    # brother_place(percorso[100:])
 
    return data


coin_oscillator = 0
def map_blit() -> list:
    ''' shows the tiles and make them touchable or not '''

    def touchable(lst, x,y):
        ''' add to the list of tangible object (tiles like dirt_img) '''
        lst.append([tile, pygame.Rect(x * 16, y * 16, 16, 16)])
    def touchable_coins(lst, x,y):
    
        lst.append(pygame.Rect(x * 16, y * 16, 16, 16))
        display.blit(coin_img, (x * 16 - scroll[0], y * 16 - scroll[1]))

    ''' blits the tiles on the display surface '''
    tile_rects = [] # this will contain the tiles position
    y = 0

    for layer in game_map: # iteration of 0 and 1... space or tile
        x = 0
        for tile in layer:
            # CONDITION TO LIMIT BLITTING OF TILES TO THE VISIBLE ONES
            right = x*16 < player_rect.x + 200 # 480
            down = y*16 < player_rect.y + 200 #320
            up = y*16 > player_rect.y - 200 # 250
            left = x* 16 > player_rect.x - 200# 200 and y*16 > player_rect.y - 200
            # if player_rect.x - 300 < x*16 < player_rect.x + 300:
            if (right and down):
                if up and left:
                    # ========================== HERE THE TILES ARE SHOWN =========== #
                    if tile == 7: # tree not tangible
                        display.blit(plat7, (x * 16 - scroll[0], y * 16 - scroll[1]))
                        tile_rects.append([tile, pygame.Rect(x * 16, y * 16, 16, 1)])
                    if tile == 6: # tree not tangible
                        display.blit(plat6, (x * 16 - scroll[0], y * 16 - scroll[1]))
                        # this is touchable the half the height
                        tile_rects.append([tile, pygame.Rect(x * 16, y * 16, 16, 1)])
                    if tile == 5: # tree not tangible
                        display.blit(tree_img, (x * 16 - scroll[0], y * 16 - scroll[1]))
                    if tile == 4: # grass tangible
                        display.blit(grass_img, (x * 16 - scroll[0], y * 16 - scroll[1]))
                        touchable(tile_rects, x, y)
                    if tile == 2:
                        touchable_coins(coin_rects, x + coin_oscillator, y)

                    if tile == 1: # diplay a tile (eventually shifted with scroll[0])
                        # show(display, dirt_img, x, y)
                        display.blit(dirt_img, (x * 16 - scroll[0], y * 16 - scroll[1]))
                        touchable(tile_rects, x, y)
                    if tile == 3:
                        display.blit(brother, (x * 16 - scroll[0], y * 16 - scroll[1]))
                x += 1 # counter for the index in the list of 0 and 1 (game_map)
        y += 1
    return tile_rects, coin_rects


def change_action(action_var,frame,new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var,frame
        


def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile[1]):
            hit_list.append([tile, tile[1]])
    return hit_list

timer = 0
def move(rect,movement,tiles):
    global timer, score

    collision_types = {'top':False,'bottom':False,'right':False,'left':False}
    rect.y += movement[1] # vertical movement, continues to fall
    hit_list = collision_test(rect,tiles)
    for tile in hit_list:
        if movement[1] > 0: # if goes down
            rect.bottom = tile[1].top # stays on top oaf the tile
            collision_types['bottom'] = True
    rect.x += movement[0]

    # COLLISION WITH COINS
    for coin in coin_rects:
        # coin.x = coin.x + randrange(1,2)
        if coin.colliderect(player_rect):
            score += 10
            coin_sound.play()
            # delete the coin from the game_map list of tiles [[0,0...]...]
            y, x = coin.y//16, coin.x//16
            game_map[y][x] = 0
    return rect, collision_types


pygame.init() # all starts here
pygame.mixer.init()
pygame.mixer.music.load("sounds/music.wav")
pygame.mixer.music.play()
click = pygame.mixer.Sound("sounds/click.ogg")
coin_sound = pygame.mixer.Sound("sounds/coin_2.wav")
jump = pygame.mixer.Sound("sounds/jump.wav")
clock = pygame.time.Clock() # for the frame rate (not to go too fast)
pygame.display.set_caption('Pygame Platformer')
WINDOW_SIZE = (900,600)
screen = pygame.display.set_mode(WINDOW_SIZE,0,32)  # Main surface
display = pygame.Surface((300, 200)) # temporary surface to scale on screen
moving_right = False # where is moving
moving_left = False
vertical_momentum = 0 # for the jump
air_timer = 0 # how long the jump is ?

true_scroll = [0,0] # the camera control
game_map = create_map() # 0 and 1... and other numbers for tile
animation_frames = {} # key = frame name, value = run_0, run_0, ... run_1...
animation_database = {} # database with a key for each action (run and idle)

animation_database['run'] = load_animation('player_animations/run',[7,7])
# the duration of each frame is different here
animation_database['idle'] = load_animation('player_animations/idle',[7,7,40])

score = 0
coins = []
class Coin:
    def __init__(self):
        self.image = pygame.image.load('coin.png').convert() # 2

dirt_img = pygame.image.load('dirt.png').convert() # 1
coin_img = Coin().image # 2
brother = pygame.image.load('brother.png').convert() # 3
grass_img = pygame.image.load('grass.png').convert() # 4
tree_img = pygame.image.load('tree.png').convert() # 5
plat6 = pygame.image.load('plat6.png').convert() # 5
plat7 = pygame.image.load('plat7.png').convert() # 5
player_action = 'idle'
player_frame = 0
player_flip = False

player_rect = pygame.Rect(160, 160, 5, 13)

fps_font = pygame.font.SysFont("Arial", 20) # a font for the fps

def steps():
    if timecnt % 16 == 0:
        click.play()
global collision_types
timecnt = 0
while True: # game loop
    timecnt += 1
    display.fill((0,0,0)) # clear screen by filling it with blue
    # screen.blit(pygame.transform.scale(display2, WINDOW_SIZE), (0,0))
    true_scroll[0] += (player_rect.x-true_scroll[0]-152)//20
    true_scroll[1] += (player_rect.y-true_scroll[1]-106)//20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])
    coin_rects = []
    tile_rects, coin_rects = map_blit()
    # tile_rects = map_blit()

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
        steps()
        player_flip = False
        player_action,player_frame = change_action(player_action,player_frame,'run')
    if player_movement[0] < 0:
        steps()
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

    display.blit(
        pygame.transform.flip(player_img,player_flip, False),
        (player_rect.x - scroll[0], player_rect.y - scroll[1]))


    for event in pygame.event.get(): # event loop
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            
            if event.key == K_SPACE:  #               restart the game
                player_rect.x = 160
                player_rect.y = 160
                game_map = create_map()

            if event.key == K_RIGHT:
                    moving_right = True
            if event.key == K_LEFT:
                    moving_left = True
            if event.key == K_UP:
                timer = 0
                jump.play()
                if air_timer < 20: # Air times goes from 0 to 5 when is standing
                                  # so when it is on the ground can jump
                    vertical_momentum = -3

            if event.key == K_DOWN:
                # collisions["bottom"] = False
                player_rect.bottom += 20
                jump.play()


        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False
    show_fps()
    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0,0))
    pygame.display.update()
    clock.tick(60)

    '''
20.01.2022
- arrow down = go down from the tile



    '''
