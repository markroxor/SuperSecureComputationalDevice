from elgamal import PrivateKey, PublicKey, generate_keys, encrypt, decrypt
import pickle
import json
from random import randint

x = generate_keys()

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
x2 = x - x1 - x0%publicKey.p

xis = [x1, x2, x0]

for i in range(3):
    with open('privateKey'+str(i)+'.key', 'w') as f:
        db = {'p': privateKey.p, 'g':privateKey.g, 'x':xis[i]}
        json.dump(db, f)


#################################################################################################################################################################################################################################

publicKey = None
privateKey = None
xis = None

with open('publicKey.key') as f:
    publicKey = json.load(f)

publicKey = PublicKey(publicKey['p'], publicKey['g'], publicKey['h'], 256)

x = 0

for i in range(3):
    with open('privateKey'+str(i)+'.key') as f:
        privateKey = json.load(f)
        x = (x + privateKey['x'])%privateKey['p']

privateKey = PrivateKey(privateKey['p'], privateKey['g'], x, 256)

cipher = encrypt(publicKey, "This is the message I want to encrypt")
print('this is ciphertext -> ', cipher)
plaintext = decrypt(privateKey, cipher)
print('\n\nthis is plaintext -> ', plaintext)

