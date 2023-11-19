#!/bin/bash

/tmp/oc project target

/tmp/oc get events -w | /listener.sh


