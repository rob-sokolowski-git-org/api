import pytest
import random
import shutil

from api.server import app
from api.types import Pong, DuckDbProcessCsvFileResponse
from env_config import CONFIG
from fastapi.testclient import TestClient


TEST_TEMP_DIR = "./tests/temp"


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def test_ping(client: TestClient):
    response = client.get("http://localhost:8000/ping", timeout=1)

    assert response.ok
    assert Pong(**response.json()).message == "PONG!"


def test_upload_csv_to_duckdb_server(client: TestClient):
    url = "http://localhost:8000/duckdb/files"

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
        assert response.ref_group.firestore_collection_name == CONFIG.firestore_duckdb_refs_collection
