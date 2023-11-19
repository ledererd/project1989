#!/bin/bash

cd docker
podman build . -t=project1989-mock-eda
podman push localhost/project1989-mock-eda:latest quay.io/dlederer/project1989-mock-eda:latest


