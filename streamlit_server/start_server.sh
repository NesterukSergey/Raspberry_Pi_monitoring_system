#!/bin/bash

DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $DIR

SCRIPT="server.py"

sudo streamlit run $SCRIPT
