from elgamal import PrivateKey, PublicKey, generate_keys, encrypt, decrypt
import pickle
import json
from random import randint

x = generate_keys(128)

publicKey = x['publicKey']
privateKey = x['privateKey']

with open('publicKey.key', 'w') as f:
    db = {'p': publicKey.p, 'g':publicKey.g, 'h':publicKey.h}
    json.dump(db, f)

with open('privateKey.key', 'w') as f:
    db = {'p': privateKey.p, 'g':privateKey.g, 'x':privateKey.x}
    json.dump(db, f)

x = privateKey.x
x0 = randint(1, x)%publicKey.p
x1 = randint(1, x)%publicKey.p
x2 = (x - x1 - x0)%publicKey.p

xis = [x1, x2, x0]

for i in range(3):
    with open('privateKey'+str(i)+'.key', 'w') as f:
        db = {'p': privateKey.p, 'g':privateKey.g, 'x':xis[i]}
        json.dump(db, f)

mis = ["4", "6", "13"]
cis = [(encrypt(publicKey, mis[0])), (encrypt(publicKey, mis[1])), (encrypt(publicKey, mis[2]))]

#for i in range(3):
#    print(mis[i], "->", cis[i], "->", (decrypt(privateKey, cis[i])))

# for i in range(3):
#     with open('message'+str(i)+'.m', 'w') as f:
#         db = {'m':int(mis[i])}
#         json.dump(db, f)

for i in range(3):
    with open('cipher'+str(i)+'.c', 'w') as f:
        db = {'c':cis[i]}
        json.dump(db, f)
        
        
        
# setting up private client and player key for final encryption for ledger post
x = generate_keys(128)
publicKey = x['publicKey']
privateKey = x['privateKey']

with open('publicClientKey.key', 'w') as f:
    db = {'p': publicKey.p, 'g':publicKey.g, 'h':publicKey.h}
    json.dump(db, f)

with open('privateClientKey.key', 'w') as f:
    db = {'p': privateKey.p, 'g':privateKey.g, 'x':privateKey.x}
    json.dump(db, f)
    

#################################################################################################################################################################################################################################

publicKey = None
privateKey = None
xis = None

with open('publicKey.key') as f:
    publicKey = json.load(f)

publicKey = PublicKey(publicKey['p'], publicKey['g'], publicKey['h'], 128)

x = 0

for i in range(3):
    with open('privateKey'+str(i)+'.key') as f:
        privateKey = json.load(f)
        x = (x + privateKey['x'])%privateKey['p']

privateKey = PrivateKey(privateKey['p'], privateKey['g'], x, 128)

cipher = encrypt(publicKey, "This")
# cipher = int(''.join(cipher.split()))

print('this is ciphertext -> ', cipher)

# cipher
plaintext = decrypt(privateKey, cipher)
print('\n\nthis is plaintext -> ', plaintext)

