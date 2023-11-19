#!/bin/bash

cd docker
podman build . -t=project1989-recovery-engine
podman push localhost/project1989-recovery-engine:latest quay.io/dlederer/project1989-recovery-engine:latest


