import json
import socket
import sys

_SOCKET_PATH = "/tmp/sandbox.sock"

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect(_SOCKET_PATH)
sock.sendall((json.dumps({"code": sys.argv[1]}) + "\n").encode())

buffer = b""
while not buffer.endswith(b"\n"):
    buffer += sock.recv(65536)

sys.stdout.write(buffer.decode())
