#!/bin/bash

DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $DIR

SCRIPT="server.py"

rm log.txt
touch log.txt
echo "Start streamlit server" >> log.txt

while true
do
  sudo streamlit run $SCRIPT

  sleep 60
  echo "Restart streamlit server" >> log.txt
done

