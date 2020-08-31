#!/bin/bash

DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $DIR

SCRIPT="refresh_server.py"

sudo python3 $SCRIPT
