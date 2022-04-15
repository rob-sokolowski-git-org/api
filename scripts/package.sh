#!/bin/bash

docker build \
  -t robsoko-api:latest\
  --file Dockerfile-Deployment \
  .
