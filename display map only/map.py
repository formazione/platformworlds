import pygame
import sys
from pygame.locals import *

map = """
oo       xxxxxxx      xx
xxxxx      o o         o
oo       ooooo        oo
oo         o o         o
oo         ooo        oo
oo       ooooooo       o
oo         o o        oo
oo         ooo     ooooo
oo         o o     o  oo
oooooooooooooooooooooooo
oooooooooooooooooooooooo
oooooooooooooooooooooooo
    """.splitlines()
tl = {}
tl["o"] = pygame.image.load('dirt.png')
tl["x"] = pygame.image.load('grass.png')
pygame.init()
pygame.display.set_caption('Game')
WINDOW_SIZE = (764,368)
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
display = pygame.Surface((WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
clock = pygame.time.Clock()

loop = 1
while loop:
    # CLEAR THE SCREEN
    display.fill((146, 244, 255))
    for event in pygame.event.get():
        if event.type == QUIT:
            loop = 0
    # Tiles are blitted  ==========================
    tile_rects = []
    y = 0
    for line_of_symbols in map:
        x = 0
        for symbol in line_of_symbols:
            if symbol != " ":
                display.blit(tl[symbol], (x * 16, y * 16))
                    # draw a rectangle for every symbol except for the empty one
            x += 1
        y += 1

    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
    pygame.display.update()
    clock.tick(60)

pygame.quit()