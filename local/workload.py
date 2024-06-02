#!/usr/bin/env python3

import signal
import sys
from time import sleep

# Set up a quick exit
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

while True:

    sleep(1)

