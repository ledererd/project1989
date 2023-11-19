#!/bin/bash

( cd mock-lightspeed && ./build.sh)
( cd recovery-engine && ./build.sh)
( cd mock-eda && ./build.sh)
( cd eda-engine && ./build.sh)
( cd dummy-workload && ./build.sh)
( cd kubeinvaders && ./build.sh)
