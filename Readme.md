# SuperSecureComputationalDevice

`gen_keys.py` will generate elgamal keys, store the FULL keys in privateKey.key has params (p,g,h) and privateKey.key with params (p,g,x)
It also splits the the key for each player in privateKey{i}.py using sum protocol II. So that individually none of the parties have any information about
the privateKey. [ONLY x from the privateKey.key is shared no other param ofc]

`player.py` should be called individually for each player with player ID as parameter ie `python player.py i` where i in {0,1,2}
each player will have access to privateKey{i}.key ONLY and will send each other the share of their privateKey's share and sum them up.
So each player will have its own sum of the shares of the shares of all the players. Summing this sum provided by all the players will provide the final privateKey.key. 

`elgamal.py` is the library used for generating elgamal keys.

`counter.py` - copy this file in your `counter` folder in the pyteal-course folder.

[refer script.sh for comment on its working]
