import pygame
from pygame.locals import *
from sys import exit
import copy

# defines the colors we may use in game
WHITE = (255, 255, 255)
GRAY  = (127, 127, 127)
BLACK = (  0,   0,   0)
GREEN = (  0, 135,   0)

# set the board
TILE_SIZE = 50
BOARD_SIZE = 8
MARGIN = 40
PIECE_RADIUS = 20

# three status of a tile
EMPTY_TILE  = "EMPTY"
WHITE_PIECE = "WHITE"
BLACK_PIECE = "BLACK"

# Set the fonts
pygame.font.init()
FONT_SIZE = 20
FONT = pygame.font.SysFont("Arial", FONT_SIZE)

# number of moves into the future the computer will check for each game mode
EASY_NUM = 1
MED_NUM = 3
HARD_NUM = 4

# reset the board as the start of the game
def board_reset(board):
    # fill the board with EMPTY_TILEs
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            board[x][y] = EMPTY_TILE

    # add four pieces at the middle of the board
    board[3][3] = WHITE_PIECE
    board[3][4] = BLACK_PIECE
    board[4][3] = BLACK_PIECE
    board[4][4] = WHITE_PIECE

# a test case that demonstrates the difference between greedy and minimax
def test_reset(board):
    # fill the board with EMPTY_TILEs
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            board[x][y] = EMPTY_TILE

    # put a certain pattern on the board to test
    board[3][5] = BLACK_PIECE
    board[3][6] = WHITE_PIECE
    board[4][5] = WHITE_PIECE
    board[3][4] = WHITE_PIECE
    board[3][3] = BLACK_PIECE

    # set the scores
    return {"WHITE":3, "BLACK":2}

# convert the screen coord to board coord
def to_board_coord(screen_x, screen_y):
    board_x = int((screen_x - MARGIN) / TILE_SIZE)
    board_y = int((screen_y - MARGIN) / TILE_SIZE)
    return board_x, board_y

# convert the board coord to screen coord
def to_screen_coord(board_x, board_y):
    screen_x = int((board_x+0.5) * TILE_SIZE + MARGIN)
    screen_y = int((board_y+0.5) * TILE_SIZE + MARGIN)
    return screen_x, screen_y

# display text on screen
def display_text(screen, string):
    # Render the text
    msg = FONT.render(string, True, BLACK)
    
    # Move it into position
    msg_rect = pygame.Rect((0, 0), msg.get_size())
    msg_rect.center = (
        to_screen_coord(BOARD_SIZE/2-0.5, BOARD_SIZE/2-0.5))
            
    # Draw a background rectangle
    pygame.draw.rect(screen, WHITE, msg_rect)
    pygame.draw.rect(screen, BLACK, msg_rect, 2)

    # Draw it
    screen.blit(msg, msg_rect)
    pygame.display.update()

# draw the board according to the board array
def draw_board(screen, board):
    # set the background green
    screen.fill(GREEN)

    # draw the board
    for x in range(BOARD_SIZE+1):
        x1 = x * TILE_SIZE + MARGIN
        y1 = MARGIN
        x2 = x * TILE_SIZE + MARGIN
        y2 = BOARD_SIZE * TILE_SIZE + MARGIN
        pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2))
    for y in range(BOARD_SIZE+1):
        x1 = MARGIN
        y1 = y * TILE_SIZE + MARGIN 
        x2 = BOARD_SIZE * TILE_SIZE + MARGIN
        y2 = y * TILE_SIZE + MARGIN
        pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2))

    # draw pieces on the board according to the board array
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            screen_x, screen_y = to_screen_coord(x,y)
            if board[x][y] == WHITE_PIECE:
                pygame.draw.circle(
                    screen, 
                    WHITE, 
                    (screen_x, screen_y), 
                    PIECE_RADIUS)
            if board[x][y] == BLACK_PIECE:
                pygame.draw.circle(
                    screen, 
                    BLACK, 
                    (screen_x, screen_y), 
                    PIECE_RADIUS)

# determine the difficulty
def difficulty_determine(SCREEN):
    # global variable to change the difficulty
    #global FUTURE_MOVES

    # 'easy' button
    easy = FONT.render('EASY', True, GRAY)
    easy_rect = easy.get_rect()
    easy_rect.center = (240, 200)

    # 'normal' button
    normal = FONT.render('NORMAL', True, GRAY)
    normal_rect = normal.get_rect()
    normal_rect.center = (240, 240)

    # 'hard' button
    hard = FONT.render('HARD', True, GRAY)
    hard_rect = hard.get_rect()
    hard_rect.center = (240, 280)

    # display the buttons
    SCREEN.blit(easy, easy_rect)
    SCREEN.blit(normal, normal_rect)
    SCREEN.blit(hard, hard_rect)

    # constantly check the events
    while True:
        for event in pygame.event.get():
            # End if exit button at top of screen is clicked
            if event.type == pygame.QUIT:
                pygame.display.quit()
                exit()
            # End if q is pressed
            elif (event.type == pygame.KEYDOWN and
                  (event.key == pygame.K_q or event.key == pygame.K_ESCAPE)):
                pygame.display.quit()
                exit()

            # if click at button, get corresponding FUTURE_MOVES to determine 
            # difficulty and get out the loop
            if event.type == MOUSEBUTTONUP:
                x,y = event.pos
                if easy_rect.collidepoint((x,y)):
                    FUTURE_MOVES = EASY_NUM
                    return FUTURE_MOVES
                elif normal_rect.collidepoint((x,y)):
                    FUTURE_MOVES = MED_NUM
                    return FUTURE_MOVES
                elif hard_rect.collidepoint((x,y)):
                    FUTURE_MOVES = HARD_NUM
                    return FUTURE_MOVES

        # update the board
        pygame.display.update()
        
# the main menu of the game including options about game mode and instructions
def main_menu(SCREEN):
    # display the instructions
    instruct_string1 = "During a play, any disks of the opponent's color"
    instruct_string2 = "that are in a straight line and bounded by the"
    instruct_string3 = "disk just placed and another disk of the current"
    instruct_string4 = "player's color are turned over to the current "
    instruct_string5 = "player's color. White makes the first move."
    instruct1 = FONT.render(instruct_string1, True, GRAY)
    instruct1_rect = instruct1.get_rect()
    instruct1_rect.center = (240, 50)
    instruct2 = FONT.render(instruct_string2, True, GRAY)
    instruct2_rect = instruct2.get_rect()
    instruct2_rect.center = (240, 70)
    instruct3 = FONT.render(instruct_string3, True, GRAY)
    instruct3_rect = instruct3.get_rect()
    instruct3_rect.center = (240, 90)
    instruct4 = FONT.render(instruct_string4, True, GRAY)
    instruct4_rect = instruct4.get_rect()
    instruct4_rect.center = (240, 110)
    instruct5 = FONT.render(instruct_string5, True, GRAY)
    instruct5_rect = instruct5.get_rect()
    instruct5_rect.center = (240, 130)
    SCREEN.blit(instruct1, instruct1_rect)
    SCREEN.blit(instruct2, instruct2_rect)
    SCREEN.blit(instruct3, instruct3_rect)
    SCREEN.blit(instruct4, instruct4_rect)
    SCREEN.blit(instruct5, instruct5_rect)

    # 'PLAYER vs COMPUTER' button
    single = FONT.render('PLAYER vs COMPUTER', True, GRAY)
    single_rect = single.get_rect()
    single_rect.center = (240, 200)

    # 'PLAYER vs PLAYER' button
    double = FONT.render('PLAYER vs PLAYER', True, GRAY)
    double_rect = double.get_rect()
    double_rect.center = (240, 240)

    # display the buttons
    SCREEN.blit(single, single_rect)
    SCREEN.blit(double, double_rect)
    
    # constantly checks the event
    while True:
        for event in pygame.event.get():
            # End if exit button at top of screen is clicked
            if event.type == pygame.QUIT:
                pygame.display.quit()
                exit()
            # End if q is pressed
            elif (event.type == pygame.KEYDOWN and
                  (event.key == pygame.K_q or event.key == pygame.K_ESCAPE)):
                pygame.display.quit()
                exit()
            # choose the mode the player clicks at
            if event.type == MOUSEBUTTONUP:
                x,y = event.pos
                if single_rect.collidepoint((x,y)):
                    return "single"
                elif double_rect.collidepoint((x,y)):
                    return "double"

        # update the screen
        pygame.display.update()    

