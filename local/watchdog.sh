#!/bin/sh

#######################################################
# Simple watchdog script that checks if the spaceinvaders game is running.
# If it's not running, then reboot the server.

if ! /usr/bin/pgrep -f spaceinvaders; then

    # Give a grace period of 10 seconds and then check again
    sleep 10

    if ! /usr/bin/pgrep -f spaceinvaders; then
        /usr/sbin/reboot now
    fi
fi

