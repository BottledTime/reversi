import pygame
from pygame.locals import *
from sys import exit
from draw import *
from move import *
import copy

# record the scores of each player
score = {"WHITE":2, "BLACK":2}

# Set the colour of the computer
OPPONENT = "BLACK"
#OPPONENT = "WHITE"

# the main process of the game
def run_game():
    # create the window
    global SCREEN
    pygame.init()
    SCREEN = pygame.display.set_mode((480, 480))

    # set the title of the window
    pygame.display.set_caption('Othello')

    # create the board array
    board = [[EMPTY_TILE] * BOARD_SIZE for i in range(BOARD_SIZE)]

    # reset the board as starting status
    board_reset(board)

    #TESTING
    # Makes starting test board to demonstrate differences between difficulties
    # of computer
    #score = test_reset(board)

    # display the instructions and let the user choose the mode
    mode = main_menu(SCREEN)

    # single player mode
    if mode == "single":
        SCREEN.fill(BLACK)
        global FUTURE_MOVES
        # let the player choose the difficulty
        FUTURE_MOVES = difficulty_determine(SCREEN)
        # draw the board
        draw_board(SCREEN, board)
        # player holds white pieces
        player = WHITE_PIECE
        start_move = 1
        # initiate gameplay against computer 
        vs_computer(board, player, start_move)

    # double player mode
    elif mode == "double":
        # draw the board
        draw_board(SCREEN, board)
        # player holds white pieces
        player = WHITE_PIECE
        # initiate gameplay against the other player
        vs_player(board, player)

# double player mode
def vs_player(board, player):
    while True:

        # determine the player and opposite
        if player == WHITE_PIECE: opposite = BLACK_PIECE
        else: opposite = WHITE_PIECE
               
        # different game event
        for event in pygame.event.get():
            # Exit if exit icon on top of screen is clicked
            if event.type == pygame.QUIT:
                pygame.display.quit()
                exit()
            # End if q is pressed
            elif (event.type == pygame.KEYDOWN and
                  (event.key == pygame.K_q or event.key == pygame.K_ESCAPE)):
                pygame.display.quit()
                exit()
            # Respond to clicks to place pieces
            elif event.type == pygame.MOUSEBUTTONUP:
                if on_click(event, board, player, opposite, score):
                    draw_board(SCREEN, board)
                    player = game_check(board, player, opposite)
        
        # update the board
        pygame.display.update()    

# single player mode
def vs_computer(board, player, start_move):
    while True:
        # determine the player and opposite
        if player == WHITE_PIECE: opposite = BLACK_PIECE
        else: opposite = WHITE_PIECE

        # determine the computer's move
        if player == OPPONENT:
            # if the current player can make a move
            if len(get_valid_spot(board, player)):
                # if the difficulty is not easy, use minimax with 
                # corresponding FUTURE_MOVES to make moves 
                if FUTURE_MOVES > 1:
                    best_move = minimax_get_move(
                        board,
                        player, 
                        opposite, 
                        start_move, 
                        FUTURE_MOVES, 
                        score)["Move"]
                # if the difficulty is easy, use greedy to make moves
                else:
                    best_move = greedy_get_move(
                        board, 
                        player, 
                        opposite, 
                        FUTURE_MOVES, 
                        score)

            # if the current player cannot make a move, switch the player
            else:
                # empty the best_move 
                best_move = ()
                # check if the game is over
                player = game_check(board, player, opposite)
                if player != OPPONENT:
                    opposite = OPPONENT

            # when there is a best_move
            if len(best_move):
                # make move at the best_move
                make_move(
                    board, 
                    player, 
                    opposite, 
                    best_move[0], 
                    best_move[1], 
                    score)
                # draw the boaard
                draw_board(SCREEN, board)
                # determine the player
                player = game_check(board, player, opposite)
                # switch the player
                if player != OPPONENT:
                    opposite = OPPONENT
        """
        # COMPUTER vs COMPUTER TESTING
        # if the current player can make a move
        else:
            if len(get_valid_spot(board, player)):
                # if the difficulty is not easy, use minimax with 
                # corresponding FUTURE_MOVES to make moves 
                if FUTURE_MOVES+1 > 1:
                    best_move = minimax_get_move(
                        board,
                        player, 
                        opposite, 
                        start_move, 
                        FUTURE_MOVES+1, 
                        score)["Move"]
                # if the difficulty is easy, use greedy to make moves
                else:
                    best_move = greedy_get_move(
                        board, 
                        player, 
                        opposite, 
                        FUTURE_MOVES+1, 
                        score)

            # if the current player cannot make a move, switch the player
            else:
                # empty the best_move 
                best_move = ()
                # check if the game is over
                player = game_check(board, player, opposite)
                if player != OPPONENT:
                    opposite = OPPONENT

            # when there is a best_move
            if len(best_move):
                # make move at the best_move
                make_move(
                    board, 
                    player, 
                    opposite, 
                    best_move[0], 
                    best_move[1], 
                    score)
                # draw the boaard
                draw_board(SCREEN, board)
                # determine the player
                player = game_check(board, player, opposite)
                # switch the player
                if player != OPPONENT:
                    opposite = OPPONENT
        #COMP vs COMP TEST end
        """            
        # different event in game
        for event in pygame.event.get():
            # End if exit box is clicked
            if event.type == pygame.QUIT:
                pygame.display.quit()
                exit()
            # End if q is pressed
            elif (event.type == pygame.KEYDOWN and
                  (event.key == pygame.K_q or event.key == pygame.K_ESCAPE)):
                pygame.display.quit()
                exit()
            # Respond to clicks to place pieces
            elif event.type == pygame.MOUSEBUTTONUP:
                if on_click(event, board, player, opposite, score):
                    draw_board(SCREEN, board)
                    player = game_check(board, player, opposite)
        # Update the board
        pygame.display.update()

# determine player of the next turn or if the game's over 
def game_check(board, player, opposite):

    # if no one can make a move, find the winner and end the game
    if len(get_valid_spot(board, opposite)) == 0:
        if len(get_valid_spot(board, player)) == 0:
            # Find out who won
            get_winner(board)

        # if only one cannot make a move, skip their turn by not changing
        # the player
        else:
            # tell user there are no moves 
            # Determine the message
            display_text(SCREEN, "  {} CANNOT MAKE A MOVE  ".format(opposite))
            pygame.time.wait(1000)
            draw_board(SCREEN, board)
            return player
                        
    # else, turn to the other player
    else: return opposite

# determine the winner according the score
def get_winner(board):
    if score["WHITE"] > score["BLACK"]:
        display_text(SCREEN, "  WHITE WINS!  ")
    elif score["BLACK"] > score["WHITE"]:
        display_text(SCREEN, "  BLACK WINS!  ")
    else:
        display_text(SCREEN, "  IT'S A DRAW!  ")

    # give player option to restart the game
    restart()

# give the player the option to restart the game
def restart():

    # make the 'MAIN MENU' button
    back = FONT.render("  MAIN MENU  ", True, BLACK)
    back_rect = pygame.Rect((0, 0), back.get_size())
    back_rect.center = (
        to_screen_coord(BOARD_SIZE/2-0.5, BOARD_SIZE/2+1))
    pygame.draw.rect(SCREEN, WHITE, back_rect)
    pygame.draw.rect(SCREEN, BLACK, back_rect, 2)

    # draw it
    SCREEN.blit(back, back_rect)

    # update the screen
    pygame.display.update()

    # constantly checks the event 
    while(True):
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
            # if the button is clicked, reset score and rerun the game
            elif event.type == pygame.MOUSEBUTTONUP:
                x,y = event.pos
                if back_rect.collidepoint((x,y)):
                    score["WHITE"] = 2
                    score["BLACK"] = 2
                    run_game()

run_game()
