#!/bin/bash

oc project target
for i in 1 2 3 4 5 6 7 8; do
    oc process -f pod-template.yaml -p WORKLOAD_NAME=workload${i} | oc create -f -
done
