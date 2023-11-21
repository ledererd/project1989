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

	if [ "${POD}" == "bigip" ]; then
		DIEROLL=$(( ( RANDOM % 3 ) ))
	   	[ $DIEROLL -eq 0 ] && REQUEST="Create F5 VIP"
		[ $DIEROLL -eq 1 ] && REQUEST="Flush F5 DNS cache"
		[ $DIEROLL -eq 2 ] && REQUEST="Reboot F5"
	fi
	if [ "${POD}" == "cisco-aci" ]; then
	       DIEROLL=$(( ( RANDOM % 3 ) ))
       	       [ $DIEROLL -eq 0 ] && REQUEST="Create a Cisco ACI VLAN"
               [ $DIEROLL -eq 1 ] && REQUEST="Create a Cisco ACI tenant"
               [ $DIEROLL -eq 2 ] && REQUEST="Create Cisco ACI link level policies"
	fi
	if [ "${POD}" == "openshift" ]; then
               DIEROLL=$(( ( RANDOM % 3 ) ))
       	       [ $DIEROLL -eq 0 ] && REQUEST="Create an OpenShift namespace"
	       [ $DIEROLL -eq 1 ] && REQUEST="Scale an OpenShift deployment"
	       [ $DIEROLL -eq 2 ] && REQUEST="Roll-back an OpenShift deployment"
	fi
	if [ "${POD}" == "nginx" ]; then
               DIEROLL=$(( ( RANDOM % 2 ) ))
               [ $DIEROLL -eq 0 ] && REQUEST="Restart an nginx server"
	       [ $DIEROLL -eq 1 ] && REQUEST="Update nginx TLS config"
	fi
	if [ "${POD}" == "sap-hana" ]; then
	       DIEROLL=$(( ( RANDOM % 3 ) ))
       	       [ $DIEROLL -eq 0 ] && REQUEST="Clear a SAP queue"
	       [ $DIEROLL -eq 1 ] && REQUEST="Backup SAP HANA"
	       [ $DIEROLL -eq 2 ] && REQUEST="Create RHEL server on Azure for SAP HANA replica"
	fi
	[ "${POD}" == "websphere" ] && REQUEST="Restart a Websphere instance"
	[ "${POD}" == "ibm-db2" ]   && REQUEST="Login to DB2"

	curl -H "Accept: application/json, text/plain, /" \
            -H "Content-Type: application/json" \
	    -X POST \
	    -s \
	    -d "{\"request\": \"${REQUEST}\", \"deployment\": \"${POD}\"}" \
	    http://eda-engine:8080/ &

done
