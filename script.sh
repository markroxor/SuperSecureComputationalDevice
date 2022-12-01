#!/usr/bin/env bash
# build the code you have written, inside the pyteal-course directory run
./build.sh contracts.crypto.counter

# inside sandbox dir run -
./sandbox/sandbox enter algod
# to enter algod docker

# get creator account address
goal account list # this will show accounts of all the addresses

# get the first address in this and set it as the var which hold the app creator account address
ONE="BECPX5HTIFDW67S4F6ZDA4DRYATIHVH5WTVIF5KHVIIDJMRDU2FDNSPV3E"

# create the app
goal app create --approval-prog /data/build/approval.teal --clear-prog /data/build/clear.teal --creator $ONE --global-ints 6 --global-byteslices 8 --local-ints 4 --local-byteslices 12

# manually note down the APP_ID and set  the variable below
APP_ID=149

# get the generated app's account address and store it in the var below
goal app info --app-id $APP_ID
APP_ACCOUNT="KYP2AVWN3KWJUXUPJ5I5ICQHPM4N23QPGM5PJBU3W7DCAOWOHIZOBF3QRE"

rm -rf player* challenge*
WAGER=5000

# again run goal account list and select any other address then the one previously used and set it as a player account
playerR_ACCOUNT="RUGHU76PQT3M2B4MSHV3RWO3T5NSXOZSIKRTZAG7LXVJJEVPQ7RDMRQHPA"

FEES=500000

# add some money to app account from the app creator account (he is rich)
goal clerk send \
    -a "$FEES" \
    -t "$APP_ACCOUNT" \
    -f "$ONE"

# app creator and player(s) must optin to the app
goal app optin --from $ONE --app-id $APP_ID
goal app optin --from $playerR_ACCOUNT --app-id $APP_ID

# remove junk
rm -rf player* challenge*

# this should be called by our MPC to send their share from OUTSIDE of algo docker.
goal app call \
    --app-id "$APP_ID" \
    -f "$ONE" \
    --app-account "$playerR_ACCOUNT" \
    --app-arg "str:accept_player_input" \
    --app-arg "str:p0" \   # since adversary is passive the honest player must call their honest params
    --app-arg "b64:MTIz" \ # base64 encoding of 123 or whatever share you want to send
    --fee "$FEES" \
    -o player-call.tx # this outputs the transaction in a file but doesnt RUN it just yet.

# the player sends the wager from their account to app account (should this be reserved?)
goal clerk send \
    -a "$WAGER" \
    -t "$APP_ACCOUNT" \
    -f "$playerR_ACCOUNT" \
    -o player-wager.tx

# need not understand everything going on below this line just yet. 
# It's just that the last rawsend command will run bo the transctions that we created above
# (the last two commands we ran)

# group transactions
cat player-call.tx player-wager.tx >| player-combined.tx
goal clerk group -i player-combined.tx -o player-grouped.tx
goal clerk split -i player-grouped.tx -o player-split.tx

# sign individual transactions
goal clerk sign -i player-split-0.tx -o player-signed-0.tx
goal clerk sign -i player-split-1.tx -o player-signed-1.tx

# re-combine individually signed transactions
cat player-signed-0.tx player-signed-1.tx >| player-signed-final.tx

# send transaction
goal clerk rawsend -f player-signed-final.tx
