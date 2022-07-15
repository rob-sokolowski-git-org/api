#!/bin/bash

docker build \
  -t fir-api:dev\
  --file Dockerfile-Dev \
  .
