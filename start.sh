#!/bin/bash

DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $DIR

SCRIPT="main.py"
echo "launching " $DIR/$SCRIPT

rm log.txt
touch log.txt
echo "Start monitoring server" >> log.txt

while true
do
  /usr/bin/python3.7 $DIR/$SCRIPT

  sleep 10
  echo "Restart monitoring server" >> log.txt
done