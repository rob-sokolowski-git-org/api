from google.cloud import storage


def test_stuff():
    storage_client = storage.Client()
    bucket_name = "test-test"
