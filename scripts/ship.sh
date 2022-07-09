#!/bin/bash

docker tag \
    robsoko-api:latest \
    gcr.io/fir-sandbox-326008/robsoko-api:latest

docker push gcr.io/fir-sandbox-326008/robsoko-api:latest

gcloud run deploy robsoko-api \
    --image gcr.io/fir-sandbox-326008/robsoko-api:latest \
    --platform managed \
    --region us-east4 \
    --memory 2048Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 1
