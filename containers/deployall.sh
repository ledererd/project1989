#!/bin/bash

oc new-project target
oc new-project project1989

#oc adm policy add-cluster-role-to-user cluster-admin system:serviceaccount:project1989:default
oc adm policy add-role-to-user admin system:serviceaccount:project1989:default -n target
oc adm policy add-role-to-user admin system:serviceaccount:project1989:default

#( cd mock-lightspeed && oc create -f mock-lightspeed.yaml )
#( cd recovery-engine && oc create -f recovery-engine.yaml )
#( cd mock-eda && oc create -f mock-eda.yaml )
#( cd eda-engine/docker && oc create configmap eda-engine-config --from-file ./config.yaml )
#( cd eda-engine && oc create -f eda-engine.yaml )
#( cd dummy-workload && ./create-all-workloads.sh )
oc create -f allin.yaml

cd kubeinvaders

oc project project1989
# Needed to get the kubeinvaders container running as root (I know, I know...)
oc adm policy add-scc-to-user anyuid -z default

# Need to create the route
oc create -f route.yaml

# Now fetch the route name
sleep 2
KI_ROUTE=$( oc get route kubeinvaders -o json | jq -r '.spec.host' )
EDA_ROUTE=$( oc get route eda-engine -o json -n project1989 | jq -r '.spec.host' )

# This is the original helm chart that we're reproducing:
#helm install kubeinvaders \
#    --set-string config.target_namespace="target" \
#    -n kubeinvaders \
#    kubeinvaders/kubeinvaders \
#    --set ingress.enabled=true \
#    --set ingress.hostName=${ROUTE} \
#    --set deployment.image.tag=v1.9.6

IMAGE="quay.io/dlederer/project1989-kubeinvaders:latest"

cat custom-deployment.yaml | \
    sed "s/kubeinvaders_endpoint_placeholder/${KI_ROUTE}/g" | \
    sed "s/lightspeed_endpoint_placeholder/${EDA_ROUTE}/g" | \
    oc create -f -

