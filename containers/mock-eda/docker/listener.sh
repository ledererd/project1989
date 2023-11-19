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

	echo "$TIME $TYPE $STATUS $THISPOD $DESC"

	POD=$( echo "$THISPOD" | sed 's^pod/^^g' )

	[ "${POD}" == "bigip" ]     && REQUEST="Create F5 VIP"
	[ "${POD}" == "cisco-aci" ] && REQUEST="Create a Cisco ACI VLAN"
	[ "${POD}" == "ibm-db2" ]   && REQUEST="Login to DB2"
	[ "${POD}" == "openshift" ] && REQUEST="Create an OpenShift namespace"
	[ "${POD}" == "cloud-lb" ]  && REQUEST="Create something"
	[ "${POD}" == "nginx" ]     && REQUEST="Restart an nginx server"
	[ "${POD}" == "sap-hana" ]  && REQUEST="Clear a SAP queue"
	[ "${POD}" == "websphere" ] && REQUEST="Restart a Websphere instance"

	curl -H "Accept: application/json, text/plain, /" \
            -H "Content-Type: application/json" \
	    -X POST \
	    -s \
	    -d "{\"request\": \"${REQUEST}\", \"deployment\": \"${POD}\"}" \
	    http://eda-engine:8080/ &

done
