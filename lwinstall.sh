#!/bin/bash

pythonexists=`apt list | grep python3`

if [ "$pythonexists" = "" ]; then
    echo "Install Python 3 to use LANwhiz"
    return 1
fi

# Install Reqiored Python libs
pip3 install napalm netmiko django

# Append parent dir to PYTHONPATH
echo "Adding parent dir to PYTHONPATH.."
DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="$PYTHONPATH:${DIR/LANwhiz/}"

echo "Happy Automating!"