#!/bin/bash

while read TIME TYPE STATUS THISPOD DESC; do

        # Filter out only the "Killing" events - this is when a pod dies
        #[ "${STATUS}" != "Killing" ] && continue

	#echo "Testing: $TIME"

        # Ignore anything that's older than a minute
        if [ `echo "${TIME}" | grep "^[0-9]*s"` ]; then
                echo "$TIME $TYPE $STATUS $THISPOD $DESC"
        else
                continue
        fi
done
