### TINCOS01 Practicum 3 - server.py ###

# Bartholomeus Petrus
# Hidde-Jan Daniëls
# Thijs Dregmans
# 2023-04-17

# version 1.0

import socket
import time

HOST = "localhost"
PORT = 1024

print("create server on "+  HOST + ":" + str(PORT))
s = socket.create_server((HOST, PORT))
s.listen()

time.sleep(1)
print("server created")

conn, addr = s.accept()

print(conn)

data = conn.recv(1024).decode() # 1024 is the buffer size

conn.sendall(data.encode("ascii")) # encode to convert a string object to a byte array

