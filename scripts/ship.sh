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
    --cpu 4 \
    --set-env-vars "ENV_NAME=production" \
    --set-env-vars "GCP_PROJECT_ID=fir-sandbox-326008" \
    --set-env-vars "BUCKET_NAME=rob-soko-api-production" \
    --set-env-vars "TEMP_DIR=./temp" \
    --set-env-vars "MAGIC_WORD_SECRETS_KEY=projects/fir-sandbox-326008/secrets/production-magic-word/versions/1" \
    --set-env-vars "GOOGLE_APPLICATION_CREDENTIALS=.private/gcloud-runner-production-key.json" \
    --set-env-vars "TEST_SECRET_SECRETS_KEY=projects/fir-sandbox-326008/secrets/test-secret/versions/1" \
    --min-instances 0 \
    --max-instances 1
