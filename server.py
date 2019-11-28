import socket
import re # regex package
import threading
from contract import Command
from serialization import serialize, deserialize

state = {}

def new_board():
  return ['1', '2', '3', '4', '5', '6', '7', '8', '9']

def room_exists(room, state):
  return room in state

def get_board(client_address, state):
  room = state[client_address]
  return state[room]["board"]

def has_winner(client_address, state):
  room = state[client_address]
  board = state[room]["board"]

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
        if first_symbol == get_symbol(client_address, state):
          return client_address
        else:
          players = state[room]["players"]
          opponent = list(filter(lambda x: x != client_address, players))[0]
          return opponent
    else:
      won = False

def no_empty_positions(board):
  return len(list(filter(lambda x: x not in ['X', 'O'], board ))) == 0

def get_opponent(client_address, state):
  room = state[client_address]
  players = state[room]["players"]
  opponent = list(filter(lambda x: x != client_address, players))
  if (len(opponent) == 1):
    opponent = opponent[0]
    return state[room][opponent]["username"]
  else:
    return None

def get_symbol(client_address, state):
  room = state[client_address]
  return state[room][client_address]["symbol"]

def game_status(client_address, state):
  room = state[client_address]
  board = state[room]["board"]
  players = state[room]["players"]
  current_turn = state[room]["current_turn"]
  two_players_connected = len(players) == 2
  game_started = board != new_board()
  winner = has_winner(client_address, state)

  if (not two_players_connected) and (not game_started):
    return 'waiting_for_opponent_to_join'
  if (not two_players_connected) and game_started:
    return 'opponent_disconnected'
  if winner == client_address:
    return 'you_won'
  if winner and (not winner == client_address):
    return 'you_lost'
  if (not winner) and no_empty_positions(board):
    return 'you_tied'
  if current_turn == client_address:
    return 'your_turn'
  else:
    return 'opponent_turn'

def join_first_player(room, player, client_address, state):
  print("join first")
  print(player)
  state[room] = {
    "board": new_board(),
     client_address: {
       "symbol": "X",
       "username": player
     },
     "players": [client_address],
     "current_turn": client_address 
  }
  state[client_address] = room 

def join_second_player(room, player, client_address, state):
  first_player = state[room]["players"][0]
  state[room][client_address] = {
    "symbol": "O",
    "username": player
  }
  state[room]["players"] = [first_player, client_address]
  state[client_address] = room

def join_room(join_room_input, client_address, state):
  room = join_room_input["room"]
  player = join_room_input["player"]
  if not room_exists(room, state):
    join_first_player(room, player, client_address, state)
  else:
    join_second_player(room, player, client_address, state)
  return {
    "board": get_board(client_address, state),
    "game_status": game_status(client_address, state),
    "opponent_id": get_opponent(client_address, state),
    "symbol": get_symbol(client_address, state)
  }

def get_game_status(client_address, state):
  room = state[client_address]
  board = state[room]["board"]
  return {
    "board": board,
    "game_status": game_status(client_address, state),
    "opponent_id": get_opponent(client_address, state)
  }

def fill_position(fill_position_input, client_address, state):
  room = state[client_address]
  symbol = state[room][client_address]["symbol"]
  board = state[room]["board"]
  position = int(fill_position_input["position"]) - 1
  board[position] = symbol
  state[room]["board"] = board
  players = state[room]["players"]
  opponent = list(filter(lambda x: x != client_address, players))[0]
  state[room]["current_turn"] = opponent
  return {
    "message": "ok"
  }

def parse_request(data):
  request = deserialize(data)
  return request["command"], request

def connection_loop(connection, client_address, state):
  try:
    while True:
      data = connection.recv(4096)
      if not data: break;
      command, command_input = parse_request(data)
      if command == Command.JOIN_ROOM.value:
        response = join_room(command_input, client_address, state)
      if command == Command.GET_GAME_STATUS.value:
        response = get_game_status(client_address, state)
      if command == Command.FILL_POSITION.value:
        response = fill_position(command_input, client_address, state)
      connection.send(serialize(response))
  finally: 
    connection.close()
    print('client disconnected')
  
class ConnectionHandlerThread (threading.Thread):
  def __init__(self, thread_id, connection, client_address, state):
    threading.Thread.__init__(self)
    self.state = state
    self.thread_id = thread_id
    self.connection = connection
    self.client_address = client_address
      
  def run(self):
    connection_loop(self.connection, self.client_address, self.state)
    
def main():
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.bind(('0.0.0.0', 8080))
  server.listen(5)
  open_connections = 0
  while True:
    connection, client_address = server.accept()
    open_connections += 1
    thread_id = "thread-{counter}".format(counter=open_connections)
    new_thread = ConnectionHandlerThread(thread_id, connection, client_address, state)
    new_thread.start()
    
main()
