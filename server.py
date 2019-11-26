import socket
import re # regex package
import threading

board = []

COMMAND_PATTERN = "(\S*)\s?(\S*)"

def serialize(data):
  return ''.join(str(x) for x in data)

def deserialize(data_str):
  return list(data_str)
    
class ConnectionHandlerThread (threading.Thread):
  def __init__(self, thread_id, connection, client_address):
    threading.Thread.__init__(self)
    self.thread_id = thread_id
    self.connection = connection
    self.client_address = client_address
      
  def run(self):
    try:
      while True:
        data = self.connection.recv(4096)
        if not data: break
        command, command_args = get_command(data)
        if command == 'get_board':
          response = get_board()
        if command == 'set_board':
          response = set_board(deserialize(command_args))
        if command == 'init_board':
          response = init_board()
        self.connection.send(serialize(response))
    finally: 
      self.connection.close()
      print 'client disconnected'  

def get_board():
  return board

def set_board(new_board):
  global board
  board = new_board
  return board

def init_board():
  return set_board(['1','2','3','4','5','6','7','8','9'])

def get_command(data):
  match = re.search(COMMAND_PATTERN, data)
  command = match.groups()[0]
  command_args = match.groups()[1]
  return command, command_args

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
