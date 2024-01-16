#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "$0")"; pwd)
echo export PATH=\"'$PATH':$SCRIPT_DIR/scripts\" >> ~/.zshrc
echo "setup ok"