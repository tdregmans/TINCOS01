import socket
from time import sleep

HOST = "localhost" #change to IP address of server
PORT = 1024

connected = False
s = socket.socket()

def connect():
    try:
        s.connect((HOST, PORT))
        connected = True
    except:
        print("Connection refused")
        connected = False
        exit()
        
def send(msg):
    s.sendall(msg.encode('ascii'))
    sleep(1)


connect()
    
send('first message')
send('second message')
send('exit')

s.close()
