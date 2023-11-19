#!/bin/bash

for job in $( oc get jobs -o name ); do
   if [[ "$( oc get "${job}" -o jsonpath="{.status.conditions[0]['status','type']}" )" != "True Complete" ]]; then
       continue
   fi

   #completionTime=$( oc get "${job}" -o jsonpath='{.status.completionTime}' )
   #if [[ "$( date -d "${completionTime}" +%s)" -lt  "$( date -d "${cutoff}" +%s )" ]]; then
       oc delete "${job}"
   #fi
done
