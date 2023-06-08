import socket
from time import sleep

HOST = "localhost" #change to IP address of server
PORT = 1024

s = socket.socket()
try:
    s.connect((HOST, PORT))
except:
    print("Connection refused")
    exit()
    
a = 'first message'
s.sendall(a.encode('ascii'))
sleep(1)

a = 'second message'
s.sendall(a.encode('ascii'))
sleep(1)

a='exit'
s.sendall(a.encode('ascii'))
sleep(1)

s.close()
