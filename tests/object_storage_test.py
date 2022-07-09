import pytest

from api import object_storage as obj
from google.cloud import storage


def test_stuff():
    test_file = "./data/president_polls.csv"
    bucket_name = "local-dev-tests"
    key = "test-blob"


    obj.send_file(path=test_file, bucket_name=bucket_name, key=key)
