#!/bin/bash

for name in bigip cisco-aci ibm-db2 sap-hana openshift nginx websphere cloud-lb; do
    EXISTS=$( ps -ef | grep "workload.py ${name}" | grep -v grep )
    [ "${EXISTS}" == "" ] && ./workload.py ${name} &
done
