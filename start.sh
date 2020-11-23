#!/bin/bash

DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $DIR

SCRIPT="main.py"
echo "launching " $DIR$SCRIPT

sudo python3.7 $SCRIPT
