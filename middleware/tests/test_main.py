"""Tests for middleware main application"""

from fastapi.testclient import TestClient

import pytest
from middleware.src.main import app, chroma, settings


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_metrics(client):
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "python_info" in res.text


def test_context_endpoint(client, monkeypatch):
    class DummyColl:
        async def get(self, ids):
            return {"ids": ids}

    monkeypatch.setattr(chroma.client, "get_collection", lambda name: DummyColl())
    res = client.get(
        "/context/test/1", headers={"Authorization": f"Bearer {settings.API_TOKEN}"}
    )
    assert res.status_code == 200
    assert res.json() == {"ids": ["test:1"]}
