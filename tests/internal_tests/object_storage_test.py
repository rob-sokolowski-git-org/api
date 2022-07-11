import pytest

from api import object_storage as obj
from google.cloud import storage
from google.cloud.storage import Bucket
import random
import time

from os.path import exists


# NB: Any file will do, we just need a file
TEST_FILE_PATH = "./data/president_polls.csv"
TEST_TEMP_DIR = "./tests/temp"


@pytest.fixture
def empty_bucket() -> storage.Bucket:
    name = f"automated-test-{int(time.time() * 1_000)}"
    yield obj.create_bucket(bucket_name=name)
    obj._delete_bucket(bucket_name=name, force=True)


def test_create_and_delete_bucket():
    name = f"automated-test-{int(time.time() * 1_000)}"
    obj.create_bucket(bucket_name=name)
    obj._delete_bucket(bucket_name=name, force=True)


def test_deleting_non_existing_raises():
    with pytest.raises(Exception):
        obj._delete_bucket(bucket_name=f"non-existing-bucket-{random.randint(0, 1_000_000)}")


def test_creating_already_created_bucket_raises(empty_bucket: Bucket):
    """Attempting to re-create an existing bucket should raise"""
    with pytest.raises(Exception):
        obj.create_bucket(bucket_name=empty_bucket.name)


def test_get_bucket(empty_bucket):
    retrieved_bucket = obj.get_bucket(bucket_name=empty_bucket.name)

    assert retrieved_bucket.name == empty_bucket.name


def test_get_non_existing_bucket_raises():
    with pytest.raises(Exception):
        obj.get_bucket(bucket_name=f"non-existing-bucket-{random.randint(0, 1_000_000)}")


def test_create_then_fetch_blob(empty_bucket: Bucket):
    """Upload, then download a file"""
    key = f"automated-test-file-{int(time.time())}.csv"
    dest = f"{TEST_TEMP_DIR}/automated-test-{int(time.time())}.csv"
    obj.create_file(path=TEST_FILE_PATH, bucket_name=empty_bucket.name, key=key)

    assert not exists(dest)
    obj.fetch_file(empty_bucket.name, key=key, dest_path=dest)
    assert exists(dest)


def test_create_blob_already_exists_quietly_overwrites(empty_bucket: Bucket):
    """Our minimally configured bucket allows us to override existing files"""
    key = f"automated-test-file-{int(time.time())}.csv"
    obj.create_file(path=TEST_FILE_PATH, bucket_name=empty_bucket.name, key=key)

    # do it again, non-error implies success - testing of creation tested elsewhere in this file!
    obj.create_file(path=TEST_FILE_PATH, bucket_name=empty_bucket.name, key=key)


def test_list_blobs(empty_bucket: Bucket):
    """lists all blobs in bucket"""
    key = f"automated-test-file-{int(time.time())}.csv"
    obj.create_file(path=TEST_FILE_PATH, bucket_name=empty_bucket.name, key=key)

    blobs = obj.list_blobs(bucket_name=empty_bucket.name)

    assert blobs[0].name == key


def test_fetch_non_existing_blob_raises(empty_bucket: Bucket):
    key = f"non-existent-blob-{random.randint(0, 1_000_000)}"
    dummy_path = f"{TEST_TEMP_DIR}/dummy.csv"

    with pytest.raises(Exception):
        obj.fetch_file(bucket_name=empty_bucket.name, key=key, dest_path=dummy_path)
