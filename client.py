import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

## Conecta a um IP em uma porta
sock.connect(('0.0.0.0', 8080))

## Envia dados (pode ser chamo multiplas vezes)
sock.send("GET /Users/lucas.mafra/hello.txt HTTP/1.1 \n Host: 0.0.0.0 \r\n")

## Recebe ate 4096 bytes de um par
from_server = sock.recv(4096)

print from_server

## Fecha a conexao
sock.close()
