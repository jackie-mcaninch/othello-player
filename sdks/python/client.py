#!/usr/bin/python

import sys
import json
import socket
import math

def gen_adj_indices(row_idx, col_idx):
  indices = []
  for i in [-1,0,1]:
    for j in [-1,0,1]:
      if (row_idx+i >= 0 and row_idx+i <8 and 
          col_idx+j >= 0 and col_idx+j <8 and
          (i != 0 or j != 0)):
        indices.append([row_idx+i, col_idx+j])
  for idx in indices:
    yield idx[0], idx[1]

def get_flipped_count(board, r, c, dir, opp):
  # walk through the line to count how many opponents pieces would be flipped
  flip_count = 0
  while True:
    r += dir[0]
    c += dir[1]
    if r>7 or r<0 or c>7 or c<0 or board[r][c]==0:
      # either boundary or an empty square has been reached - invalid move
      return 0 
    elif board[r][c] == opp:
      # another opponent piece has been encountered - add 1 to score
      flip_count += 1
      #print(flip_count)
    else:
      # a player's own piece has been encountered - total and return points
      #print("encountered opp piece at [{}][{}]".format(r, c))
      return flip_count

def get_moves(player, board, rec_depth):
  # set opponent code
  opp = 3-player

  # initialize all moves to be invalid (0) - any other value denotes how many pieces would be flipped 
  moves = [[0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0]]

  # only allow moves which are empty squares and touch an opponent's piece
  for r in range(8):
    for c in range(8):
      curr_square = board[r][c]

      # test if the square has already been played
      if curr_square > 0:
        continue 

      # test if it touches an opponent
      for adj_r, adj_c in gen_adj_indices(r, c):
          adj_square = board[adj_r][adj_c]
          if adj_square == opp:
            
            # if so, this is a candidate to be a valid move
            dir = [adj_r-r, adj_c-c] # will signify a vector pointing in the direction of flipping
            moves[r][c] += get_flipped_count(board, r, c, dir, opp)
            
            # adjust move scores by recursively predicting opponent's next moves
            if rec_depth>0:
              moves = weighted_by_opp_pos(r, c, player, moves, board, rec_depth-1)
  
  # add weighting for piece location
  moves = weighted_by_loc(player, moves, board)
  return moves

def weighted_by_loc(player, moves, board):

  # add weights depending on piece placement
  for r in range(8):
    for c in range(8):
      # increase score when piece is placed on board edge (increase twice for corners)
      if r==0 or r==7:
        moves[r][c] = moves[r][c] * 1.25
      if c==0 or c==7:
        moves[r][c] = moves[r][c] * 1.25
      
      # decrease score when piece may allow the opponent to take an edge square
      if r==1 or r==6:
        moves[r][c] = moves[r][c] * 0.9
      if c==1 or c==6:
        moves[r][c] = moves[r][c] * 0.9
  return moves

def weighted_by_opp_pos(r, c, player, moves, board, rec_depth):
  # create a copy of board for opponent, assuming player chooses [r, c] 
  opp = 3-player
  opp_board = [row[:] for row in board]
  opp_board[r][c] = player

  # predict the opponent's move
  opp_moves = get_moves(opp, opp_board, rec_depth)

  # compare the scores head-to-head
  o_max = find_max_points(opp_moves)
  p_max = find_max_points(moves)

  # weight player's score to reflect the move's advantage over opponent
  ratio = (moves[p_max[0]][p_max[1]])/(opp_moves[o_max[0]][o_max[1]]+0.0001) # add 0.0001 to avoid divide by zero, still good estimate
  moves[r][c] *= ratio 
  return moves

def find_max_points(moves):
  max_r = 0
  max_c = 0
  for r in range(8):
    for c in range(8):
      if moves[r][c] >= moves[max_r][max_c]:
        max_r = r
        max_c = c
  return [max_r, max_c]

def get_move(player, board):
  # user defines how many moves to look ahead
  depth = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1]) else 0

  # determine moves and their effectiveness
  moves = get_moves(player, board, depth)

  # choose the move with the highest score index
  return find_max_points(moves)

def prepare_response(move):
  response = '{}\n'.format(move).encode()
  print('sending {!r}'.format(response))
  return response

if __name__ == "__main__":
  port = int(sys.argv[2]) if (len(sys.argv) > 2 and sys.argv[2]) else 1337
  host = sys.argv[3] if (len(sys.argv) > 3 and sys.argv[3]) else socket.gethostname()

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    sock.connect((host, port))
    print('Connected successfully!')
    while True:
      data = sock.recv(1024)
      if not data:
        print('connection to server closed')
        break
      json_data = json.loads(str(data.decode('UTF-8')))
      board = json_data['board']
      maxTurnTime = json_data['maxTurnTime']
      player = json_data['player']
      #print(player, maxTurnTime, board)

      move = get_move(player, board)
      response = prepare_response(move)
      sock.sendall(response)
  finally:
    sock.close()
