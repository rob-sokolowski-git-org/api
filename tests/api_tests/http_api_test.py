import random

import pytest
from fastapi.testclient import TestClient

from api.server import app
from api.types import Pong, DuckDbProcessCsvFileResponse, DuckDbTableRefsResponse, DuckDbTableRefGroupResponse
import shutil

from env_config import CONFIG

TEST_TEMP_DIR = "./tests/temp"


@pytest.fixture(scope="module")
def client():
    import requests
    return requests


# TARGET_HOST = "http://localhost:8000"  # local dev
TARGET_HOST = "http://host.docker.internal:8080"  # local gunicorn
# TARGET_HOST = "https://api.robsoko.tech92383278"

def test_ping(client: TestClient):
    response = client.get(f"{TARGET_HOST}/ping", timeout=1)

    assert response.ok
    assert Pong(**response.json()).message == "PONG!"


def test_upload_csv_to_duckdb_server(client: TestClient):
    url = f"{TARGET_HOST}/duckdb/files"
    original_path = "./data/president_polls.csv"

    # randomly generate table_ref to ensure uniqueness for testing, then copy data to that name
    table_ref = f"president_polls_{random.randint(0, 1_000_000)}"
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
        assert response.ref_group.bucket_name == CONFIG.bucket_name


def test_table_ref_endpoints(client: TestClient):
    # beg region setup
    url = f"{TARGET_HOST}/duckdb/files"
    original_path = "./data/president_polls.csv"
    table_ref = f"president_polls_{random.randint(0, 1_000_000)}"
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
