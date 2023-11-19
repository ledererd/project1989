#!/bin/bash

while read TIME TYPE STATUS THISPOD DESC; do

	# Filter out only the "Killing" events - this is when a pod dies
	[ "${STATUS}" != "Killing" ] && continue

        # Ignore anything that's older than a minute
        if [ `echo "${TIME}" | grep "^[0-9]*s"` ]; then
                echo "$TIME $TYPE $STATUS $THISPOD $DESC"
        else
                continue
        fi

	#echo "$TIME $TYPE $STATUS $THISPOD $DESC"

	POD=$( echo "$THISPOD" | sed 's^pod/^^g' )

	curl -H "Accept: application/json, text/plain, /" \
            -H "Content-Type: application/json" \
	    -X POST \
	    -s \
	    -d "{\"request\": \"Create F5 VIP\", \"deployment\": \"${POD}\"}" \
	    http://eda-engine:8080/ &

done
