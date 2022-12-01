import socket            
import sys, json
from random import randint
import threading
from time import sleep

# if the player crashes, everything will timeout in 100 secs and no communication will take place
# none of the parties will send ANYTHING to smart contract(SC) until they have ALL the
# required values
socket.setdefaulttimeout(100)

player = sys.argv[1]

HOST = "127.0.0.1"
PORT = 8080

print("I have access to my share of the secret key in file ", 'privateKey'+str(player)+'.key')
# key part
with open('privateKey'+str(player)+'.key') as f:
    privateKey = json.load(f)

x = privateKey['x']

print('my secret is', x)

# using SUM protocol II
# TODO use gadgets here to do whatever
x0 = randint(1, x)
x1 = randint(1, x)
x2 = x - x1 - x0
xs = [x0, x1, x2]

# # message part
# with open('message'+str(player)+'.m') as f:
#     message = json.load(f)

# m = message['m']

# print('my message is', m)

# # split into shares
# m0 = randint(1, int(m))
# m1 = randint(1, int(m))
# m2 = int(m) - m1 - m0
# ms = [m0, m1, m2]

# # print shares for sanity
# for i in range(3):
#     print(ms[i])

# cipher part
with open('cipher'+str(player)+'.c') as f:
    message = json.load(f)

c = message['c']

print('my cipher is', c)

# split into shares
c0 = randint(1, c)
c1 = randint(1, c)
c2 = c - c1 - c0
cs = [c0, c1, c2]

# print shares for sanity
for i in range(3):
    print(cs[i])

# using SUM protocol II
# TODO use gadgets here to do whatever

    
def receive_and_send_to_smart_contract():
    expecting_players = []
    keys = [xs[-1]]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind((HOST, PORT+ int(player)))
        s.listen()

        # keep waiting until it gets input of the other two players.
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
    # TODO send to smart contract the local computation, here
    print('sum', sum([ int(k) for k in keys]))

background_thread = threading.Thread(target=receive_and_send_to_smart_contract)
background_thread.daemon = True
background_thread.start()

# iterate over each player's server and send them their share
# of the share that I have.
for i in range(2):
    other_player = (int(player) + i + 1)%3
    while 1:
        sleep(1)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                # if the other player's server is up, send their share to them.
                s.connect((HOST, PORT+other_player))
            except:
                # if the other player's server is still not up yet, wait for it.
                continue

            print('sending to ', other_player, xs[i])
            s.sendall((str(player)+" I am "+str(player) + " sending data to " + str(other_player ) + " data is -> " + str(xs[i])).encode('utf-8'))

        break

# wait for background process to finish
background_thread.join()
