from enum import Enum
from pykson import JsonObject, StringField, ListField, BooleanField, EnumIntegerField, ObjectField,Pykson

commands_list = ['JOIN_ROOM', 'GET_GAME_STATUS', 'FILL_POSITION']
Command = Enum('Command', " ".join(commands_list))

class Request(JsonObject):
  command = EnumIntegerField(enum=Command)

class JoinRoomRequest(Request):
  player = StringField()
  room = StringField()

class JoinRoomResponse(JsonObject):
  board = ListField(str)
  game_status = StringField()
  opponent_id = StringField()
  symbol = StringField()

class GetGameStatusRequest(Request):
  command = Command.JOIN_ROOM

class GetGameStatusResponse(JsonObject):
  board = ListField(str)
  game_status = StringField()
  
pson = Pykson()
