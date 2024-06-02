#!/bin/sh


pkill -f "python3 ./workload.py"
pkill -f server-lightspeed.py
pkill -f eda-engine-server.py
pkill -f server-mock-kube.py
pkill -f server-recovery-engine.py

