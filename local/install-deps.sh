#!/bin/sh

#####################################################################
# Change our working directory to the dir containing this script
DIR=$( dirname $0 )

#####################################################################
sudo apt install python3-websockets python3-yaml python3-fastapi -y

#####################################################################
echo "[autostart]
1=lxterminal -e sh ${DIR}/run-all.sh" >> /home/damo/.config/wayfire.ini
