#!/bin/sh

#####################################################################
# Change our working directory to the dir containing this script
cd $( dirname $0 )
DIR=$( pwd )

#####################################################################
sudo apt install python3-websockets python3-yaml python3-fastapi -y

#####################################################################
echo "[autostart]
1=lxterminal -e sh ${DIR}/run-all.sh" >> /home/damo/.config/wayfire.ini


#####################################################################
# Set background
/usr/bin/pcmanfm --set-wallpaper=${DIR}/open-graph_brand-campaign.jpg --wallpaper-mode=fit
