import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from interface.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def set_key_env(monkeypatch):
    monkeypatch.setenv("INTERNAL_API_KEY", "very-secret-key")


def test_requires_header():
    resp = client.get("/internal/agents/capabilities")
    assert resp.status_code == 403


def test_returns_capabilities():
    mock_payload = {
        "response": {
            "timestamp": "2025-05-19T05:35:00Z",
            "capabilities": {"ping": ["ping", "respond"]},
        }
    }
    with patch("interface.internal.capabilities.send_request", return_value=mock_payload):
        resp = client.get(
            "/internal/agents/capabilities",
            headers={"X-Internal-Key": "very-secret-key"},
        )
    assert resp.status_code == 200
    assert resp.json() == mock_payload["response"]
