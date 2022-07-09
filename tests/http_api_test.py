import pytest
from fastapi.testclient import TestClient

from api.server import app
from api.types import Pong


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def test_ping(client: TestClient):
    response = client.get("http://localhost:8000/ping", timeout=1)

    assert response.ok
    assert Pong(**response.json()).message == "PONG!"


def test_upload_file(client: TestClient):
    url = "http://localhost:8000/files"
    path = "./data/president_polls.csv"

    with open(path, 'r') as f:
        r = client.post(
            url,
            files={"file": (f.name, f, "multipart/form-data")},
        )

        assert r.ok
