import random
import pytest
import shutil

import utils
from api.types import Pong, DuckDbProcessCsvFileResponse, DuckDbTableRefsResponse, DuckDbTableRefGroupResponse, \
    DuckDbQueryRequest, DuckDbQueryResponse
from fastapi.testclient import TestClient

TEST_TEMP_DIR = "./tests/temp"

# TODO: When I do the CloudBuild work these should be set via env files
TARGET_HOST = "http://localhost:8000"  # local dev
# TARGET_HOST = "http://host.docker.internal:8080"  # local gunicorn
# TARGET_HOST = "https://api.robsoko.tech"  # production


@pytest.fixture(scope="module")
def client():
    """
    This fixture is funky, but useful

    If you wish to run these api tests and also debug the service in a debugger, set
    TARGET_HOST to localhost. This will return a TestClient which mimcs the `request`
    modules API, to communicate with an in-memory instance of the service.

    To run these tests against production, or a separate container already running locally, just
    specify a non localhost url (without trailing /).

    returns a requests-module-like object.. sometimes dynamic typing is pretty cool!
    """
    if TARGET_HOST == "http://localhost:8000":
        # load app, wrap it in a requests-module-like TestClient object
        from api.server import app
        return TestClient(app)
    else:
        # target is external, use standard requests module for tests
        import requests
        return requests


def test_ping(client: TestClient):
    response = client.get(f"{TARGET_HOST}/ping", timeout=1)

    assert response.ok
    assert Pong(**response.json()).message == "PONG!"


def test_upload_csv_to_duckdb_server(client: TestClient):
    url = f"{TARGET_HOST}/duckdb/files"
    original_path = "./data/president_polls.csv"

    # randomly generate table_ref to ensure uniqueness for testing, then copy data to that name
    table_ref = f"automated_test_president_polls_{random.randint(0, 1_000_000)}"
    copied_path = f"{TEST_TEMP_DIR}/{table_ref}.csv"

    shutil.copy(original_path, copied_path)

    with open(copied_path, 'r') as f:
        r = client.post(
            url,
            data={
                "duckdb_table_ref": table_ref
            },
            files={
                "file": (f.name, f, "multipart/form-data"),
            },
        )

        assert r.ok
        response = DuckDbProcessCsvFileResponse(**r.json())

        assert response.ref_group.ref == table_ref
        assert response.ref_group.parquet_key == f"{table_ref}.parquet"

        # TODO: Once Cloud Build envs are implemented, this assert must vary according to env
        # assert response.ref_group.bucket_name == CONFIG.bucket_name


def test_table_ref_endpoints(client: TestClient):
    # begin region setup
    url = f"{TARGET_HOST}/duckdb/files"
    original_path = "./data/president_polls.csv"
    table_ref = f"automated_test_president_polls_{random.randint(0, 1_000_000)}"
    copied_path = f"{TEST_TEMP_DIR}/{table_ref}.csv"
    shutil.copy(original_path, copied_path)
    with open(copied_path, 'r') as f:
        _ = client.post(
            url,
            data={
                "duckdb_table_ref": table_ref
            },
            files={
                "file": (f.name, f, "multipart/form-data"),
            },
        )
    # end region setup
    url_list_refs_endpoint = f"{TARGET_HOST}/duckdb/table_refs"
    url_fetch_ref_group_endpoint = f"{TARGET_HOST}/duckdb/table_refs/{table_ref}"

    # our newly uploaded table's table_ref appears in the list of table_refs
    r1 = client.get(url_list_refs_endpoint)
    refs_response = DuckDbTableRefsResponse(**r1.json())
    assert table_ref in refs_response.refs

    # we can get more detailed metadata for that table_ref
    r2 = client.get(url_fetch_ref_group_endpoint)
    ref_group_response = DuckDbTableRefGroupResponse(**r2.json())
    assert ref_group_response.ref_group.ref == table_ref


def test_dubckdb_query(client: TestClient):
    # begin region test setup
    file_upload_url = f"{TARGET_HOST}/duckdb/files"
    original_path = "./data/president_polls.csv"

    # randomly generate table_ref to ensure uniqueness for testing, then copy data to that name
    table_ref = f"automated_test_president_polls_{random.randint(0, 1_000_000)}"
    copied_path = f"{TEST_TEMP_DIR}/{table_ref}.csv"
    shutil.copy(original_path, copied_path)

    with open(copied_path, 'r') as f:
        r = client.post(
            file_upload_url,
            data={
                "duckdb_table_ref": table_ref
            },
            files={
                "file": (f.name, f, "multipart/form-data"),
            },
        )
    # begin region test setup
    query_duckdb_url = f"{TARGET_HOST}/duckdb"

    r = client.post(
        query_duckdb_url,
        json=DuckDbQueryRequest(
            query_str = f"select * from {table_ref}",
            fallback_table_refs=[table_ref],
            allow_blob_fallback=True,
        ).dict()
    )

    assert r.ok
    # deserialize to expected response type
    resp = DuckDbQueryResponse(**r.json())
    assert len(resp.columns) > 0


def test_dev_util_log_check(client: TestClient):
    url = f"{TARGET_HOST}/dev_utils/log_check"

    r1 = client.post(
        url,
        headers={"X-magic-word":""},
    )
    # verify we are denied without magic word
    assert r1.status_code == 401

    r2 = client.post(
        url,
        headers={"X-magic-word": utils.read_magic_word()},
    )

    assert r2.ok
    # But verifying logs is a manual step, go check!
