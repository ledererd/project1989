#!/bin/bash

################################################################
# THIS IS THE ORIGINAL WAY TO RUN KUBEINVADERS
# **** NO LONGER USED ****
################################################################

helm repo add kubeinvaders https://lucky-sideburn.github.io/helm-charts/
helm repo update

oc create namespace kubeinvaders

oc project kubeinvaders

oc adm policy add-scc-to-user anyuid -z kubeinvaders

# Need to create the route
oc create -f route.yaml

# Now fetch the route name
ROUTE=$( oc get route kubeinvaders -o json | jq -r '.spec.host' )

helm install kubeinvaders \
    --set-string config.target_namespace="target" \
    -n kubeinvaders \
    kubeinvaders/kubeinvaders \
    --set ingress.enabled=true \
    --set ingress.hostName=${ROUTE} \
    --set deployment.image.tag=v1.9.6

