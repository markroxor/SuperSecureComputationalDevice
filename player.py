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
x0 = randint(1, x)%privateKey['p']
x1_ = randint(1, x)%privateKey['p']
x2_ = (x - x1_ - x0)%privateKey['p']
xs = [x0, x1_, x2_]

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

# print('my cipher is', c)

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

global x1,y2,x2,k1,k2,R1,R2,y1

k1 = None
k2 = None
R1 = None
R2 = None

def receive(method):
    global x1,y2,x2,k1,k2,R1,R2,y1
    expecting_players = []
    data_r = [x]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # print('reception server running at ', (HOST, PORT+ int(player)), method)
        s.bind((HOST, PORT+ int(player)))
        s.listen()

        # keep waiting until it gets input of the other two players.
        while not (len(expecting_players) >= 2 and (int(player) + 1)%3 in expecting_players and (int(player) + 2)%3 in expecting_players):
            conn, addr = s.accept()
            # print("got conn")
            with conn:
                while True:
                    # sleep(1)
                    # print('waiting to recieve at', (HOST, PORT+ int(player)), method)
                    data = conn.recv(1024)
                    if not data:
                        continue
                    other_player = int(data.split()[0])
                    method = data.split()[1]
                    # print('got method', method)

                    if method == b'pk' and other_player not in expecting_players:
                        # print(" got -> ", data)
                        data_r.append(data.split()[-1])
                        expecting_players.append(other_player)

                    if method == b'get_xy_share':
                        if player == '0':
                            y1 = int(data.split()[-1])
                            # print('RECV: y1', y1)
                        if player == '1':
                            x2 = int(data.split()[-1])
                            # print('RECV: x2', x2)

                    if method == b'get_k':
                        if player == '0':
                            k2 = int(data.split()[-1])
                            # print('RECV: k2', k2)
                        if player == '1':
                            k1 = int(data.split()[-1])
                            # print('RECV: k1', k1)

                    if method == b'get_r':
                        if player == '0':
                            R2 = data.split()[-1]
                            # print('RECV: R2', R2)
                            # print('set R2')
                        if player == '1':
                            R1 = data.split()[-1]
                            # print('RECV: R1', R1)
                    break


            if method != b'pk':
                break
    
    # print('data received is ', method, data_r)
    # TODO send to smart contract the local computation, here
    # print('sum', method, sum([ int(k) for k in data_r]))

# pk_background_thread = threading.Thread(target=receive, args=('pk',))
# pk_background_thread.daemon = True
# pk_background_thread.start()

# iterate over each player's server and send them their share
# of the share that I have.

def send(msg, other_player, method):
    # other_player = (int(player) + other_player)%3
    while 1:
        # sleep(1)
        # print('SEND: waiting for ', (HOST, PORT+other_player), method)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                # if the other player's server is up, send their share to them.
                s.connect((HOST, PORT+other_player))
            except:
                # if the other player's server is still not up yet, wait for it.
                continue

            # print('SEND: sending to ', other_player, ' the msg -> ', msg)
            to_s = str(player)+" "+method+" " + str(msg)
            # print("SEND:", method, msg)
            s.sendall((to_s).encode('utf-8'))
            # print("SENT:", to_s)

        break

# for i in range(2):
#     i+=1
#     send(x, (int(player) + i)%3, 'pk')

# wait for background process to finish
# pk_background_thread.join()


print("$"*80)


ms = [7, 3]
NUM_BITS = 3
s1s = []
i = 0
# while ms[i]:

# 5 bit num only
for _ in range(NUM_BITS):
    s1s.append(ms[i]%2)
    ms[i] //= 2

s2s = []
i = 1
for _ in range(NUM_BITS):
    s2s.append(ms[i]%2)
    ms[i] //= 2

prod = 0
for i in range(NUM_BITS):
    for j in range(NUM_BITS):
        if player == '0':
            # s1s[i] 
            # print('here p0')
            with open("0s_pre_sharedbits.json") as f:
                precomps = json.load(f)
            
            # print(precomps)
            c = precomps['c']
            bc = precomps['bc']

            x = s1s[i]
            x1 = randint(0, 1)
            x2 = (x - x1)%2
            # print('x', x,'x1', x1, 'x2', x2)

            thread = threading.Thread(target=receive, args=('get_xy_share',))
            thread.daemon = True
            thread.start()
            send(x2, 1, 'get_xy_share')
            thread.join()
            y1 = y1
            # print('y1', y1)
            # send(x, 1)

            xs = []
            xs.append(((x1+0)%2)*((y1+0)%2))
            xs.append(((x1+0)%2)*((y1+1)%2))
            xs.append(((x1+1)%2)*((y1+0)%2))
            xs.append(((x1+1)%2)*((y1+1)%2))

            c_dash = (x1*2+y1)
            k1 = c_dash^c

            thread = threading.Thread(target=receive, args=('get_k',))
            thread.daemon = True
            thread.start()
            send(k1, 1, 'get_k')
            thread.join()
            k2 = k2
            # print('k2', k2)

            R1 = []
            for i_ in range(4):
                R1.append(str(precomps[str((k2+i_)%4)]^xs[i_]))
            # print()
            R1 = ','.join(R1)

            thread = threading.Thread(target=receive, args=('get_r',))
            thread.daemon = True
            thread.start()
            send(R1, 1, 'get_r')
            thread.join()
            R2 = R2

            xy = int(R2.split(b',')[c_dash]) ^ bc
            # print("got prod", xy)
            # print('i j prod', i, j, xy,xy*2**(i+j), s1s[i], s2s[j]  )
            prod += xy*2**(i+j)


        if player == '1':
            with open("1s_pre_sharedbits.json") as f:
                precomps = json.load(f)
            
            c = precomps['c']
            bc = precomps['bc']

            y = s2s[j]
            y1 = randint(0, 1)
            y2 = (y - y1)%2
            # print('y', y, 'y1', y1, 'y2', y2)

            thread = threading.Thread(target=receive, args=('get_xy_share',))
            thread.daemon = True
            thread.start()
            send(y1, 0, 'get_xy_share')
            thread.join()
            x2 = x2
            # send(x, 1)

            xs = []
            xs.append(((x2+0)%2)*((y2+0)%2))
            xs.append(((x2+0)%2)*((y2+1)%2))
            xs.append(((x2+1)%2)*((y2+0)%2))
            xs.append(((x2+1)%2)*((y2+1)%2))

            c_dash = (x2*2+y2)
            k2 = c_dash^c

            thread = threading.Thread(target=receive, args=('get_k',))
            thread.daemon = True
            thread.start()
            send(k2, 0, 'get_k')
            thread.join()
            k1 = k1

            R2 = []
            for i_ in range(4):
                R2.append(str(precomps[str((k1+i_)%4)]^xs[i_]))
            R2 = ','.join(R2)

            thread = threading.Thread(target=receive, args=('get_r',))
            thread.daemon = True
            thread.start()
            send(R2, 0, 'get_r')
            thread.join()
            R1 = R1

            xy = int(R1.split(b',')[c_dash]) ^ bc
            # print("got prod", xy)
            # print('i j prod', i, j)
            # print( xy,xy*2**(i+j), s1s[i], s2s[j]  )

            prod += xy*2**(i+j)

print(prod)

