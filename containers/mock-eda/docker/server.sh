#!/bin/bash

/tmp/oc project target

/tmp/oc get events -w -n target | /listener.sh


