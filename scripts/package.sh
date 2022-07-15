#!/bin/bash

docker build \
  -t fir-api:latest\
  --file Dockerfile-Deployment \
  .
