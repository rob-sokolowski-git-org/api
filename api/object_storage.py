from google.cloud import storage
import typing as t

# Just playing with an idea of not using classes, and using modules instead.. eh, why not?
_CLIENT: storage.Client = storage.Client()


def create_bucket(bucket_name: str) -> storage.Bucket:
    return _CLIENT.create_bucket(bucket_or_name=bucket_name)


def get_bucket(bucket_name: str) -> storage.Bucket:
    return _CLIENT.get_bucket(bucket_or_name=bucket_name)


def create_file(path: str, bucket_name: str, key: str) -> None:
    bucket = _CLIENT.bucket(bucket_name=bucket_name)
    blob = bucket.blob(blob_name=key)
    blob.upload_from_filename(filename=path)


def fetch_file(bucket_name: str, key: str, dest_path: str):
    bucket = _CLIENT.bucket(bucket_name=bucket_name)
    blob = bucket.blob(key)
    blob.download_to_filename(dest_path)


def list_blobs(bucket_name: str) -> t.List[storage.Blob]:
    return [b for b in _CLIENT.list_blobs(bucket_or_name=bucket_name)]


def _delete_bucket(bucket_name: str, force: bool=False):
    """I wrote this intending use to be limited to testing cleanup. In general, I don't want the service
    deleting data (yet)"""
    bucket = _CLIENT.get_bucket(bucket_or_name=bucket_name)
    bucket.delete(force=force)
