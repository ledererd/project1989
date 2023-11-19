#!/bin/bash


# If there's an error, then don't bomb out
set +e

export DISPLAY=:0

xset s noblank  # Don't activate screen saver
xset s off      # Don't activate screen saver
xset -dpms      # Don't blank the video device

# Hide the cursor after 5 seconds of inactivity
unclutter -idle 5 -root &


# Make sure Chromium profile is marked clean, even if it crashed
if [ -f /home/$USER/.config/chromium/Default/Preferences ]; then
    sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' /home/$USER/.config/chromium/Default/Preferences
    sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' /home/$USER/.config/chromium/Default/Preferences

#    cat /home/$USER/.config/chromium/Default/Preferences | jq -r . | \
#        sed "s/\"bottom.*/\"bottom\": $(xrandr | grep \* | cut -d' ' -f4 | cut -d'x' -f2),/" | \
#        sed "s/\"right.*/\"right\": $(xrandr | grep \* | cut -d' ' -f4 | cut -d'x' -f1),/" | \
#	    > /home/$USER/.config/chromium/Default/Preferences-clean
#    mv /home/$USER/.config/chromium/Default/Preferences{-clean,}
#    cat /home/$USER/.config/chromium/Default/Preferences

fi

# Run chromium in kioks mode
/usr/bin/chromium-browser --noerrdialogs --disable-infobars --start-fullscreen $( cat /home/$USER/app-location.txt ) &
