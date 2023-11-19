#!/bin/bash

oc project target
for name in bigip cisco-aci ibm-db2 sap-hana openshift nginx websphere cloud-lb; do
    oc process -f pod-template.yaml -p WORKLOAD_NAME=${name} | oc create -f -
done
