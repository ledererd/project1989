#!/bin/bash

cd docker
podman build . -t=project1989-dummy-workload
podman push localhost/project1989-dummy-workload:latest quay.io/dlederer/project1989-dummy-workload:latest


