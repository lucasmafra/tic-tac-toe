from enum import Enum

commands_list = ['JOIN_ROOM', 'GET_GAME_STATUS', 'FILL_POSITION']
Command = Enum('Command', " ".join(commands_list))
