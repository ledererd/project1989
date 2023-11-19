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

	[ "${POD}" == "bigip" ]     && DESC = "Create F5 VIP"
	[ "${POD}" == "cisco-aci" ] && DESC = "Create a Cisco ACI VLAN"
	[ "${POD}" == "ibm-db2" ]   && DESC = "Login to DB2"
	[ "${POD}" == "openshift" ] && DESC = "Create an OpenShift namespace"
	[ "${POD}" == "cloud-lb" ]  && DESC = "Create something"
	[ "${POD}" == "nginx" ]     && DESC = "Restart an nginx server"
	[ "${POD}" == "sap-hana" ]  && DESC = "Clear a SAP queue"
	[ "${POD}" == "websphere" ] && DESC = "Restart a Websphere instance"

	curl -H "Accept: application/json, text/plain, /" \
            -H "Content-Type: application/json" \
	    -X POST \
	    -s \
	    -d "{\"request\": \"${DESC}\", \"deployment\": \"${POD}\"}" \
	    http://eda-engine:8080/ &

done
