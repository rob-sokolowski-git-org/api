#!/bin/bash

docker build \
  -t robsoko-api:dev\
  --file Dockerfile-Dev \
  .
