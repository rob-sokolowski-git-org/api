from google.cloud import storage

import os

# Just playing with an idea of not using classes, and using modules instead.. eh, why not?
_CLIENT: storage.Client = storage.Client()

def create_bucket(bucket_name: str):
    _CLIENT.create_bucket(bucket_or_name=bucket_name)


def send_file(path: str, bucket_name: str, key: str):
    bucket = _CLIENT.bucket(bucket_name=bucket_name)
    blob = bucket.blob(blob_name=key)
    blob.upload_from_filename(filename=path)


def fetch_file(bucket_name: str, key: str, file_ptr):
    pass


def list_blobs(bucket_name: str):
    pass
