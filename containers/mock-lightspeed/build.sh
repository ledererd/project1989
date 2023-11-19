#!/bin/bash

cd docker
podman build . -t=project1989-mock-lightspeed
podman push localhost/project1989-mock-lightspeed:latest quay.io/dlederer/project1989-mock-lightspeed:latest


