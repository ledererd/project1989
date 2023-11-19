#!/bin/bash

if [ $# -ne 1 ]; then
	echo "Syntax: $0 <workload name>"
	exit 1
fi

WORKLOAD=$1

oc project target

oc process -f pod-template.yaml -p WORKLOAD_NAME=${WORKLOAD} | oc create -f -
