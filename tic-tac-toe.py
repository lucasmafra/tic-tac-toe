import os
import socket
from pykson import JsonObject, StringField, ListField, BooleanField, Pykson

def clear():
  os.system( 'clear' )

class SetBoardInput(JsonObject):
  board = ListField(str)

class JoinRoomInput(JsonObject):
  player = StringField()
  room = StringField()

class JoinRoomOutput(JsonObject):
  board = ListField(str)
  is_opponent_connected = BooleanField()
  opponent_id = StringField()
  is_my_turn = BooleanField()


def display_board(board):
  print('  |   |   ')
  print(board[0]+' | '+board[1]+' | '+board[2])
  print('  |   |   ')
  print('---------')
  print('  |   |   ')
  print(board[3]+' | '+board[4]+' | '+board[5])
  print('  |   |   ')
  print('---------') 
  print('  |   |   ')
  print(board[6]+' | '+board[7]+' | '+board[8])
  print('  |   |   ')
 
def display_status(status, room, opponent_id):
  if status == 'waiting_for_opponent_to_join':
    print("There's no opponent yet. Invite another player to join the game -> Room id: {room}".format(room = room))

  if status == 'opponent_disconnected':
    print('{opponent} left the room. Waiting for {opponent} to reconnect...'.format(opponent = opponent_id))

  if status == 'player_won':
    print('Kudos, you won the game!')

  if status == 'opponent_won':
    print('{opponent} won the game'.format(opponent = opponent_id))

  if status == 'draw':
    print('Game finished, no winner.')

  if status == 'my_turn':
    print("It's your turn.")    

  if status == 'opponent_turn':
    print("Waiting for {opponent} to play...".format(opponent = oponnent_id))

  if status == 'room_is_full':
    print("Room {room} is full :(".format(room = room))


def is_empty(board):
  return len([el for el in board if el not in ['X', 'O']]) == 0

def init_socket():
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect(('0.0.0.0', 8080))
  return sock

def close_socket(sock):
  sock.close()  

def to_bytes(string):
  bytes(string, 'utf-8')

def from_bytes(b):
  b.decode('utf-8')

def serialize(data):
  return Pykson().to_json(data)

def deserialize(json_str, model):
  return Pykson().from_json(json_str, model)

def get_board(sock):
  sock.send(to_bytes('get_board'))
  return deserialize(sock.recv(4096))

def set_board(new_board, sock):
  sock.send(to_bytes('set_board ' + serialize(new_board)))
  return deserialize(from_bytes(sock.recv(4096)))

def init_board(sock):
  sock.send(to_bytes('init_board'))
  return deserialize(from_bytes(sock.recv(4096)))

def join_room(player, room, sock):
  join_room_input = JoinRoomInput(player=player, room=room)
  sock.send(to_bytes('join_room ' + serialize(join_room_input)))
  join_room_output = deserialize(from_bytes(sock.recv(4096)), JoinRoomOutput)
  

def prompt_player_name():
  player_name = input('Choose your username: ')
  return player_name

def prompt_room():
  room = input('Type the room you want to join (or create): ')
  return room

def player_input(player, board):
  player_symbol = ['X','O']
  correct_input = True
  position = int(input('player {playerNo} chance! Choose field to fill ({symbol}): '.format(playerNo = player +1, symbol = player_symbol[player]))) - 1

  if board[position] == 'X' or board[position] == 'O':
    correct_input = False
    
  if not correct_input:
    print("Position already equipped")
    player_input(player, board)
  else:
    board[position] = player_symbol[player] 
    return board
 
def has_winner(board):
  player_symbol = ['X','O']
  winning_positions =[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
  for check in winning_positions:
    first_symbol = board[check[0]]
    if first_symbol != ' ':
      won = True
      for point in check:
        if board[point] !=  first_symbol:
          won = False
          break
      if won:
        if first_symbol == player_symbol[0]:
          print('player 1 won')
        else:
          print('player 2 won')
        break
    else:
      won = False
  if won:
    return 0
  else:
    return 1
 
def main():
  sock = init_socket()
  player = prompt_player_name()
  room = prompt_room()
  board, is_opponent_connected, opponent_id, is_my_turn = join_room(player, room, sock)
  empty = is_empty(board)
  status = build_status(board, is_opponent_connected, is_my_turn, empty)

  while not empty and not has_winner(board):
    clear()
    display_board(board)
    display_status(status, room, opponent_id)
    if is_my_turn:
      board = player_input(player, board)
      set_board(board, sock)
    else:
      wait_for_opponent_turn(sock)
    board, is_opponent_connected, opponent_id, is_my_turn = get_game_status(sock)
    empty = is_empty(board)
    status = build_status(board, is_opponent_connected, is_my_turn, empty)

  display_status(status, room, opponent_id)
  close_socket(sock)

main()
