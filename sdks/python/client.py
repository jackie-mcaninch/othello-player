#!/usr/bin/python

import sys
import json
import socket

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
      # either boundary or an empty square has been reached
      return 0 
    elif board[r][c] == opp:
      # another opponent piece has been encountered
      flip_count += 1
    else:
      # a player's own piece has been encountered - total and return points
      return flip_count




def get_valid_moves(player, board):
  # set opponent code
  opp = 3-player

  #initialize all moves to be invalid
  # invalid move = 0, any other value denotes how many pieces would be flipped 
  moves = [[0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0]]

  # only allow moves which are empty and touch an opponent's piece
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
  print(moves)
  return moves

def find_max_points(move_points):
  max_r = -1
  max_c = -1
  for r in range(8):
    for c in range(8):
      if move_points[r][c] > move_points[max_r][max_c]:
        max_r = r
        max_c = c
  return [max_r, max_c]



def get_move(player, board):
  # determine valid moves
  valid_moves = get_valid_moves(player, board)

  # TODO determine best move
  return [2,3]#find_max_points(valid_moves)

def prepare_response(move):
  response = '{}\n'.format(move).encode()
  print('sending {!r}'.format(response))
  return response

if __name__ == "__main__":
  port = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1]) else 1337
  host = sys.argv[2] if (len(sys.argv) > 2 and sys.argv[2]) else socket.gethostname()

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    sock.connect((host, port))
    while True:
      data = sock.recv(1024)
      if not data:
        print('connection to server closed')
        break
      json_data = json.loads(str(data.decode('UTF-8')))
      board = json_data['board']
      maxTurnTime = json_data['maxTurnTime']
      player = json_data['player']
      print(player, maxTurnTime, board)

      move = get_move(player, board)
      response = prepare_response(move)
      sock.sendall(response)
  finally:
    sock.close()
