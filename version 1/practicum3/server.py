import socket

HOST = ""
PORT = 1024

s = socket.create_server((HOST, PORT))
print("socket ready")
s.listen()
conn, addr = s.accept()
print("Connection accepted from ", addr)

while(True):
    data = conn.recv(1024).decode()
    if(data!=""):
        print("Received: " + data)
    if(data.startswith("exit")):
        break
s.close()
