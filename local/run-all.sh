#!/bin/sh

#####################################################################
# Change our working directory to the dir containing this script
cd $( dirname $0 )
DIR=$( pwd )


#####################################################################
# Update the config file with the correct directory
sed -i "s^BASEDIR:.*^BASEDIR: ${DIR}^g" ./config.yaml

#####################################################################
# Start up all of the dummy workloads
./create-all-workloads.sh

#####################################################################
# Make sure the streaming output file is set
[ ! -f /tmp/yamlstream.txt ] && cp yamlstream.txt /tmp/yamlstream.txt

#####################################################################
# Start up all of the servers if required
pgrep -f server-lightspeed.py || ./server-lightspeed.py 8090 &
pgrep -f server-recovery-engine.py || ./server-recovery-engine.py 8091 ./config.yaml &
pgrep -f eda-engine-server.py || ./eda-engine-server.py 8092 ./config.yaml &
pgrep -f server-mock-kube.py || ./server-mock-kube.py 8093 ./config.yaml &

sleep 2

#####################################################################
# Run the game forever.  The loop is here in case the game crashes.
while /bin/true; do
    ./spaceinvaders-pi-local.py
    sleep 5
done


