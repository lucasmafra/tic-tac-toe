import os
import socket
from contract import Command
from serialization import serialize, deserialize

def clear():
  os.system('clear')

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
 
def display_status(status, opponent_id, room):
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

  if status == 'your_turn':
    print("It's your turn.")    

  if status == 'opponent_turn':
    print("Waiting for {opponent} to play...".format(opponent = oponnent_id))

  if status == 'room_is_full':
    print("Room {room} is full :(".format(room = room))

def init_socket():
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect(('0.0.0.0', 8080))
  return sock

def close_socket(sock):
  sock.close()  

def join_room(player, room, sock):
  request = {
    "command": Command.JOIN_ROOM.value,
    "player": player,
    "room": room
  }
  sock.send(serialize(request))
  response = deserialize(sock.recv(4096))
  return response["board"], response["game_status"], response["opponent_id"], response["symbol"]
  
def refresh_game_status(sock):
  request = { 
    "command": Command.GET_GAME_STATUS.value
  }
  sock.send(serialize(request))
  response = deserialize(sock.recv(4096))
  return response["board"], response["game_status"]

def fill_position(position, sock):
  request = {
    "command": Command.FILL_POSITION.value,
    "position": position
  }
  sock.send(serialize(request))
  deserialize(sock.recv(4096))

def prompt_player_name():
  return input('Choose your username: ')

def prompt_room():
  return input('Type the room you want to join (or create): ')
1
def prompt_position(symbol):
  return input('Choose field to fill ({symbol}): '.format(symbol = symbol))

def game_not_finished(game_status):
  return game_status not in ['won', 'lost', 'tied']

def main():
  sock = init_socket()
  player = prompt_player_name()
  room = prompt_room()
  board, game_status, opponent_id, symbol = join_room(player, room, sock)

  while game_not_finished(game_status):
    clear()
    display_board(board)
    display_status(game_status, opponent_id, room)
    if game_status == 'your_turn':
      position = prompt_position(symbol)
      fill_position(position, sock)
    board, game_status = refresh_game_status(sock)

  display_status(status, room, opponent_id)
  close_socket(sock)

main()
