#!/bin/bash

cd docker
podman build . -t=project1989-eda-engine
podman push localhost/project1989-eda-engine:latest quay.io/dlederer/project1989-eda-engine:latest


