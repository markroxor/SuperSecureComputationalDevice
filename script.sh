#!/usr/bin/env bash
# change the name of the counter folder to crpto
# copy the counter.py from the repo directory to the crypto folder in the pyteal course 
# copy couter.py to 
# build the code you have written, inside the pyteal-course directory run
./build.sh contracts.crypto.counter

# inside sandbox dir run -
./sandbox/sandbox enter algod
# to enter algod docker

# get creator account address
goal account list # this will show accounts of all the addresses

# create new accounts
goal account new  # goal account rename Unnamed-0 player3
goal account new
goal account new

# get the first address in this and set it as the var which hold the app creator account address
ONE="4FVP7PJWTHE635K5THXOOVXFOZWHFZU7TFCNTNCQMSTCRAN6UAPV2EZ5XE"
playerR_ACCOUNT1="JX3CTF2TK7AEUH33F7MUILMOCNWO27C3B2SPK544LTPCEEZHBWY5VSISZI"
playerR_ACCOUNT2="J76CCECUR3WRXNGH55HLJB2FWI2M75SQP72CIR6NYET67H6DZ5PTR7N4II"
playerR_ACCOUNT3="7S4BKCVFTUT2NGLWM4JXJIZZCD353QI6RUDAOVBQHWTN2SYS7XH7P3D34Y"

# give them money
goal clerk send \
    -a "1000000" \
    -t "$playerR_ACCOUNT1" \
    -f "$ONE"
goal clerk send \
    -a "1000000" \
    -t "$playerR_ACCOUNT2" \
    -f "$ONE"
goal clerk send \
    -a "1000000" \
    -t "$playerR_ACCOUNT3" \
    -f "$ONE"

# create the app
goal app create --approval-prog /data/build/approval.teal --clear-prog /data/build/clear.teal --creator $ONE --global-ints 6 --global-byteslices 8 --local-ints 4 --local-byteslices 12

# manually note down the APP_ID and set  the variable below
APP_ID=144

# get the generated app's account address and store it in the var below
goal app info --app-id $APP_ID
APP_ACCOUNT="7KNVZBECKGSPAPROX6HXECHG4XIWOAL3I7DO6QOOUPCYARV32LYFMG44KA"

# UPDATE CONFIG.SH with ALL THE CORRECT VALS
rm -rf player* challenge*
# WAGER=5000

# again run goal account list and select any other address then the one previously used and set it as a player account
# playerR_ACCOUNT="LCUYBMLTYTJZ22ZJQMTXBMUA2ZLXLWUO3L63NLC5ZHMKFF4O5EF7HZKD2I"

FEES=500000

# add some money to app account from the app creator account (he is rich)
goal clerk send \
    -a "10000000000" \
    -t "$APP_ACCOUNT" \
    -f "$ONE" 

# app creator and player(s) must optin to the app
goal app optin --from $ONE --app-id $APP_ID
goal app optin --from $playerR_ACCOUNT1 --app-id $APP_ID
goal app optin --from $playerR_ACCOUNT2 --app-id $APP_ID
goal app optin --from $playerR_ACCOUNT3 --app-id $APP_ID

goal app read --app-id $APP_ID --global --guess-format
# remove junk
rm -rf player* challenge*

# this should be called by our MPC to send their share from OUTSIDE of algo docker.
# goal app call --app-id "$APP_ID" -f "$APP_ACCOUNT" --app-account "$playerR_ACCOUNT1" --app-arg "str:accept_player_input" --app-arg "str:p0" --app-arg "str:cipher1" --fee "$FEES" -o player-call.tx 
# goal app call --app-id "$APP_ID" -f "$APP_ACCOUNT" --app-account "$playerR_ACCOUNT2" --app-arg "str:accept_player_input" --app-arg "str:p1" --app-arg "str:cipher1" --fee "$FEES" -o player-call.tx
# goal app call --app-id "$APP_ID" -f "$APP_ACCOUNT" --app-account "$playerR_ACCOUNT3" --app-arg "str:accept_player_input" --app-arg "str:p2" --app-arg "str:cipher1" --fee "$FEES" -o player-call.tx 
# this outputs the transaction in a file but doesnt RUN it just yet.

# the player sends the wager from their account to app account (should this be reserved?)
# goal clerk send -a "3333000000" -t "$playerR_ACCOUNT3" -f "$ONE" -o player-wager.tx

# need not understand everything going on below this line just yet. 
# It's just that the last rawsend command will run bo the transctions that we created above
# (the last two commands we ran)

# group transactions
# cat player-call.tx player-wager.tx >| player-combined.tx
# goal clerk group -i player-combined.tx -o player-grouped.tx
# goal clerk split -i player-grouped.tx -o player-split.tx

# # sign individual transactions
# goal clerk sign -i player-split-0.tx -o player-signed-0.tx
# goal clerk sign -i player-split-1.tx -o player-signed-1.tx

# # re-combine individually signed transactions
# cat player-signed-0.tx player-signed-1.tx >| player-signed-final.tx

# # send transaction
# goal clerk rawsend -f player-signed-final.tx
