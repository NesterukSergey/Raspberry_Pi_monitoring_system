#!/bin/bash

DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $DIR

SCRIPT="refresh_server.py"

sleep 5
echo "Start streamlit autorefresh" >> log.txt

while true
do
  sudo python3 $SCRIPT

  sleep 60
  echo "Restart streamlit autorefresh" >> log.txt
done