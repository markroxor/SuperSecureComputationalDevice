
# import socket


# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.bind((HOST, PORT))
#     s.listen()
#     conn, addr = s.accept()
#     with conn:
#         print(f"Connected by {addr}")
#         while True:
#             data = conn.recv(1024)
#             if not data:
#                 break
#             print(data , 'data')
#             # conn.sendall(data)

# import sys
# sys.exit(0)

# first of all import the socket library
import socket            
import sys, json
from random import randint
from elgamal import PrivateKey, PublicKey, generate_keys, encrypt, decrypt

player = sys.argv[1]


HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 8080   # Port to listen on (non-privileged ports are > 1023)


print("i have access to partial key in file ", 'privateKey'+str(player)+'.key')
with open('privateKey'+str(player)+'.key') as f:
    privateKey = json.load(f)


x = privateKey['x']

print('my secret is', x)
x0 = randint(1, x)
x1 = randint(1, x)
x2 = x - x1 - x0
xs = [x0, x1, x2]

socket.setdefaulttimeout(100)
    

def receive_and_print():
    expecting_players = []
    keys = [xs[-1]]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind((HOST, PORT+ int(player)))
        s.listen()

        while not (len(expecting_players) >= 2 and (int(player) + 1)%3 in expecting_players and (int(player) + 2)%3 in expecting_players):
            conn, addr = s.accept()
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    other_player = int(data.split()[0])

                    if other_player not in expecting_players:
                        print(" got -> ", data)
                        keys.append(data.split()[-1])
                        expecting_players.append(other_player)
                        break
    
    print('keys are ', keys)
    print('sum', sum([ int(k) for k in keys]))


import threading
background_thread = threading.Thread(target=receive_and_print)
background_thread.daemon = True
background_thread.start()

import socket
from time import sleep

for i in range(2):
    other_player = (int(player) + i + 1)%3
    # print('other player is ', other_player)
    while 1:
        sleep(1)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((HOST, PORT+other_player))
            except:
                continue

            print('sending to ', other_player)
            s.sendall((str(player)+" I am "+str(player) + " sending data to " + str(other_player ) + " data is -> " + str(xs[i])).encode('utf-8'))
            # data = s.recv(1024)
        # print('breaki9ng')
        break
background_thread.join()
# print(f"Received {data!r}")

sys.exit(0)
while True: 
    try:
        c, addr = s.accept()    
    except socket.timeout:
        print('timeout')
    
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)

    print ('Got connection from', addr )

    c.send('Thank you for connecting'.encode())

    c.close()
   
#   break


import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8080  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello, world")
    data = s.recv(1024)

print(f"Received {data!r}")
