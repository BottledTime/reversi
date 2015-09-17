import pygame
from pygame.locals import *
from sys import exit
from draw import *
import copy

# three status of tiles
EMPTY_TILE  = "EMPTY"
WHITE_PIECE = "WHITE"
BLACK_PIECE = "BLACK"

# return the pieces to be flipped
def piece_to_flip(board, player, start_x, start_y):
    flip = []

    # if the spot already has a piece on it, return empty list
    if board[start_x][start_y] != EMPTY_TILE:
        return flip

    # set player
    if player == WHITE_PIECE:
        opposite = BLACK_PIECE
    elif player == BLACK_PIECE:
        opposite = WHITE_PIECE

    # checks every direction 
    for x_delta in [-1, 0, 1]:
        for y_delta in [-1, 0, 1]:
            # next tile on the direction
            x, y = start_x, start_y
            x += x_delta
            y += y_delta

            # In the board, find the first consecutive tile in this 
            # direction that does not have an opponent's piece on it, 
            # if the player's piece is put there. Add all the 
            # opponent's pieces on that dirction to flip list
            if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
                while board[x][y] == opposite:
                    if 0 <= x+x_delta < 8 and 0 <= y+y_delta < 8:
                        x += x_delta
                        y += y_delta
                    else: break
                if board[x][y] == player:
                    while (x-x_delta, y-y_delta) != (start_x, start_y):
                        x -= x_delta
                        y -= y_delta
                        flip.append((x,y))            
    return flip

# find the valid spots to put a piece
def get_valid_spot(board, player):
    valid_spot = []

    # checks the whole board, and returns all the spots that can flip
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            flip = piece_to_flip(board, player, x, y)
            if len(flip)>0:
                valid_spot.append((x,y))
    return valid_spot

# make a move at certain tile and handle the score
def make_move(board, player, opposite, start_x, start_y, score):
    flip = piece_to_flip(board, player, start_x, start_y)

    # if cannot flip, return False   
    if len(flip) == 0:
        return False
    
    # put a piece at given tile
    board[start_x][start_y] = player

    # handle the score
    score[player] += len(flip) + 1
    score[opposite] -= len(flip)

    # flip the pieces
    for x, y in flip:
        board[x][y] = player

    # return True for successfully make a mvoe
    return True

# determine what happens with a click
def on_click(event, board, player, opposite, score):
    # make sure we have focus and that it was the left mouse button
    if (event.type == pygame.MOUSEBUTTONUP
        and event.button == 1
        and pygame.mouse.get_focused()):
        board_x, board_y = to_board_coord(event.pos[0], event.pos[1])

        # if in the board and can make a move, then make the move and 
        # return True
        if (event.pos[0] > MARGIN 
            and event.pos[1] > MARGIN 
            and board_x <= 7 
            and board_y <= 7
            and make_move(board, player, opposite, board_x, board_y, score)):
            return True
        # otherwise, return False
        else: return False

# computer's greedy aglorithm of making moves
def greedy_get_move(board, player, opposite, future_moves, score):
    # initialize best_score
    best_score = {player: 0, opposite: 0}
    best_move = ()
    
    # set the old_score as the score before virtual moves
    old_score = dict()
    old_score[player] = score[player]
    old_score[opposite] = score[opposite]
    
    # make a virtual board
    virtual_board = copy.deepcopy(board)

    # go through the whole board where can make a move, find the highest 
    # score and store it to best_score and store the location of best move
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if make_move(virtual_board, player, opposite, x, y, score):
                if score[player] > best_score[player]:
                    best_score[player] = score[player]
                    best_score[opposite] = score[opposite]
                    best_move = (x, y)
                virtual_board = copy.deepcopy(board)
                score[player] = old_score[player]
                score[opposite] = old_score[opposite]

    # return best_score if the difficulty is not easy
    if future_moves > 1:
        return best_score
    # otherwise, return best_mvoe
    else:
        return best_move

# computer's move using minimax aglorithm with FUTURE_MOVES ahead
def minimax_get_move(board, player, opposite, move_count, 
                     future_moves, score):
    # initialize best_sore and best_move
    best_score = {player:0, opposite:0}
    best_move = ()

    # set the old_score as the score before virtual moves
    new_score = dict()
    old_score = dict()
    old_score[player] = score[player]
    old_score[opposite] = score[opposite]
    
    # copy the board to virtual board
    virtual_board = copy.deepcopy(board)
       
    # checks the whole board where can make a move, make a virtual move there
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if make_move(virtual_board, player, opposite, x, y, score):
                # after the virtual move, checks if the opponent can make 
                # a move based on FUTURE_MOVES, assume the opponent uses 
                # corresponding aglorithm and find the move that has the 
                # highest score
                if len(get_valid_spot(virtual_board, opposite)): 
                    # if there's more than one more move to check
                    if (move_count + 1) < future_moves:
                        new_score = minimax_get_move(
                            virtual_board,
                            opposite,
                            player,
                            (move_count+1), 
                            future_moves, 
                            score)
                    # if it's last move being checked
                    else:
                        new_score = greedy_get_move(
                            virtual_board,
                            opposite,player, 
                            future_moves, 
                            score)

                # if opposite cannot make a move after virtual move, skip
                # their move and check for another move computer can make
                elif len(get_valid_spot(virtual_board, player)):
                    if (move_count + 1) < future_moves:
                        # if there's more than one more move to check
                        new_score = minimax_get_move(
                            virtual_board,
                            player,
                            opposite,
                            (move_count+1), 
                            future_moves, 
                            score)
                    else:
                        # if it's the last move being checked
                        new_score = greedy_get_move(
                            virtual_board,
                            player,
                            opposite, 
                            future_moves, 
                            score)

                # if neither can make a move, set new_score to current score
                else: 
                    
                    # Didn't have time to check if following method works:
                    # If move_count is 1, then this is the next move the
                    # computer can make, so if it's score is greater, it
                    # makes the move and wins the game. Any greater than 
                    # 1, and it's too much of a gamble on other player 
                    # making desired move to allow win
                    if move_count == 1:
                        if score[player] > score[opposite]:
                            # do next line instead of following
                            best_move = (x, y)
                            return {"Move": best_move}
                            """
                            # make this move to win
                            make_move(
                              board, 
                              player, 
                              opposite, 
                              x, 
                              y, 
                              score)
                            # draw the board
                            draw_board(SCREEN, board)
                            # set winning screen
                            game_check(board, player, opposite)
                    # otherwise, set the new_score as equal to the score
                    """
                    new_score = score
                
                # set the highest score to best_score and store best move
                if new_score[player] > best_score[player]:
                    best_score[player] = new_score[player]
                    best_score[opposite] = new_score[opposite]
                    best_move = (x, y)

                # reset virtual board and score
                virtual_board = copy.deepcopy(board)
                score[player] = old_score[player]
                score[opposite] = old_score[opposite]

    # return the best move and the best score of player and opposite
    return {player:best_score[player], 
            opposite:best_score[opposite], 
            "Move":best_move}

