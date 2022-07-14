import logging
import sys

from api.object_storage import BlobStorage

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def upload_creds():
    storage = BlobStorage()

    # 1 per environment
    bucket_name = "rob-soko-api-maintenance"
    local_creds_filename = "service-runner-local-dev-creds.json"
    ci_creds_filename = "service-runner-ci-creds.json"
    production_creds_filename = "service-runner-production-creds.json"

    storage.create_file(path=f"./.private/{local_creds_filename}", key=local_creds_filename, bucket_name=bucket_name)
    storage.create_file(path=f"./.private/{ci_creds_filename}", key=ci_creds_filename, bucket_name=bucket_name)
    storage.create_file(path=f"./.private/{production_creds_filename}", key=production_creds_filename, bucket_name=bucket_name)

    logging.info(f"Uploaded creds file for all environments to bucket '{bucket_name}'")


if __name__ == "__main__":
    upload_creds()
