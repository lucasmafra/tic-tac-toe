import socket
import re # regex package
import threading
from contract import Command
from serialization import serialize, deserialize

def new_board():
  return ['1', '2', '3', '4', '5', '6', '7', '8', '9']

def join_room(join_room_input):
  return {
    "board": new_board(),
    "game_status": "your_turn",
    "opponent_id": "min",
    "symbol": "X"
  }

def get_game_status():
  return {
    "board": new_board(),
    "game_status": "your_turn"
  }

def fill_position(fill_position_input):
  return {
    "message": "ok"
  }
    
def parse_request(data):
  request = deserialize(data)
  return request["command"], request

def connection_loop(connection):
  try:
    while True:
      data = connection.recv(4096)
      if not data: break;
      command, command_input = parse_request(data)
      if command == Command.JOIN_ROOM.value:
        response = join_room(command_input)
      if command == Command.GET_GAME_STATUS.value:
        response = get_game_status()
      if command == Command.FILL_POSITION.value:
        response = fill_position(command_input)
      connection.send(serialize(response))
  finally: 
    connection.close()
    print('client disconnected')
  
class ConnectionHandlerThread (threading.Thread):
  def __init__(self, thread_id, connection, client_address):
    threading.Thread.__init__(self)
    self.thread_id = thread_id
    self.connection = connection
    self.client_address = client_address
      
  def run(self):
    connection_loop(self.connection)
    
def main():
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.bind(('0.0.0.0', 8080))
  server.listen(5)
  open_connections = 0
  while True:
    connection, client_address = server.accept()
    open_connections += 1
    thread_id = "thread-{counter}".format(counter=open_connections)
    new_thread = ConnectionHandlerThread(thread_id, connection, client_address)
    new_thread.start()
    
main()
