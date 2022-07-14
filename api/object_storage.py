import logging
import time
import typing as t

from google.cloud.storage import Client, Bucket, Blob


class BlobStorage:
    def __init__(self):
        self._client: Client = Client()

    def create_bucket(self, bucket_name: str) -> Bucket:
        return self._client.create_bucket(bucket_or_name=bucket_name)

    def get_bucket(self, bucket_name: str) -> Bucket:
        return self._client.get_bucket(bucket_or_name=bucket_name)

    def create_file(self, path: str, bucket_name: str, key: str) -> None:
        tic = time.perf_counter()
        bucket = self._client.bucket(bucket_name=bucket_name)
        blob = bucket.blob(blob_name=key)
        blob.upload_from_filename(filename=path)
        toc = time.perf_counter()
        logging.info(f"Created blob '{key}'. It took {toc - tic} secs")

    def fetch_file(self, bucket_name: str, key: str, dest_path: str):
        tic = time.perf_counter()
        bucket = self._client.bucket(bucket_name=bucket_name)
        blob = bucket.blob(key)
        blob.download_to_filename(dest_path)
        toc = time.perf_counter()
        logging.info(f"Fetched blob '{key}'. It took {toc-tic} secs")

    def list_blobs(self, bucket_name: str) -> t.List[Blob]:
        return [b for b in self._client.list_blobs(bucket_or_name=bucket_name)]

    def _delete_bucket(self, bucket_name: str, force: bool=False):
        """I wrote this intending use to be limited to testing cleanup. In general, I don't want the service
        deleting data (yet)"""
        bucket = self._client.get_bucket(bucket_or_name=bucket_name)
        bucket.delete(force=force)
