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

	[ "${POD}" == "bigip" ]     && REQUEST="Create F5 VIP"
	[ "${POD}" == "bigip" ]     && REQUEST="Flush F5 DNS cache"
	[ "${POD}" == "bigip" ]     && REQUEST="Reboot F5"
	[ "${POD}" == "cisco-aci" ] && REQUEST="Create a Cisco ACI VLAN"
	[ "${POD}" == "cisco-aci" ] && REQUEST="Create a Cisco ACI tenant"
	[ "${POD}" == "cisco-aci" ] && REQUEST="Create Cisco ACI link level policies"
	[ "${POD}" == "ibm-db2" ]   && REQUEST="Login to DB2"
	[ "${POD}" == "openshift" ] && REQUEST="Create an OpenShift namespace"
	[ "${POD}" == "openshift" ] && REQUEST="Scale an OpenShift deployment"
	[ "${POD}" == "openshift" ] && REQUEST="Roll-back an OpenShift deployment"
	[ "${POD}" == "nginx" ]     && REQUEST="Restart an nginx server"
	[ "${POD}" == "nginx" ]     && REQUEST="Update nginx TLS config"
	[ "${POD}" == "sap-hana" ]  && REQUEST="Clear a SAP queue"
	[ "${POD}" == "sap-hana" ]  && REQUEST="Backup SAP HANA"
	[ "${POD}" == "sap-hana" ]  && REQUEST="Create RHEL server on Azure for SAP HANA replica"
	[ "${POD}" == "websphere" ] && REQUEST="Restart a Websphere instance"

	curl -H "Accept: application/json, text/plain, /" \
            -H "Content-Type: application/json" \
	    -X POST \
	    -s \
	    -d "{\"request\": \"${REQUEST}\", \"deployment\": \"${POD}\"}" \
	    http://eda-engine:8080/ &

done
