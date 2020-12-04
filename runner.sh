#!/bin/bash

#This script should be called PORT IP [DEV/PROD] COMMAND [ARGS...]
#This script is necessary because supervisor only accepts an execuble with arguments, and passed on '|' ( pipes) and other commands as arguments to the first script.
#It will execute COMMAND [ARGS...] and pipe standard out into carrot.py

PORT=$1
IP=$2
BROKER=$3
MATCH=$4
REDIS=$5
REDIS_PASS=$6
COMMAND=$7

echo "Executing  unbuffer -p $COMMAND "${@:8}"  |  python  /home/steam/cringer/carrot.py  -p $PORT -b $BROKER -r $REDIS -q $REDIS_PASS -h $IP -m $MATCH"
eval unbuffer -p $COMMAND "${@:8}"  |  python  /home/steam/cringer/carrot.py  -p $PORT -b $BROKER -r $REDIS -q $REDIS_PASS -h $IP -m $MATCH