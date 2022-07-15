import logging
import sys

from api.object_storage import BlobStorage

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def upload_creds():
    storage = BlobStorage()
    bucket_name = "project-fir-api-maintenance"

    # Local bucket intentionally omitted, but any future envs should be added below. This is to keep
    # local developer (more elevated) rights off publicly hosted buckets.
    ci_creds_filename = "service-runner-ci-creds.json"
    production_creds_filename = "service-runner-production-creds.json"

    storage.create_file(path=f"./.private/{ci_creds_filename}", key=ci_creds_filename, bucket_name=bucket_name)
    storage.create_file(path=f"./.private/{production_creds_filename}", key=production_creds_filename, bucket_name=bucket_name)

    logging.info(f"Uploaded creds JSON file for ci and production environments to bucket '{bucket_name}'")


if __name__ == "__main__":
    upload_creds()
