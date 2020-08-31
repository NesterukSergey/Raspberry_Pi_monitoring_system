#!/bin/bash

DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $DIR

echo "Deleting all the collected data"

sudo rm -rf logs/ data/
sudo rm board.txt
