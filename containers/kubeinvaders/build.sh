#!/bin/bash

cd kubeinvaders
podman build . -t=project1989-kubeinvaders
podman push localhost/project1989-kubeinvaders:latest quay.io/dlederer/project1989-kubeinvaders:latest

