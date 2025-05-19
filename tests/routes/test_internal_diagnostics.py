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
    resp = client.get("/internal/agents/diagnostics")
    assert resp.status_code == 403


def test_returns_diagnostics():
    mock_payload = {
        "response": {
            "timestamp": "2025-05-19T04:55:21Z",
            "agents": [],
            "orchestrator": {"uptime": 1, "queue_size": 0, "active_tasks": 0},
            "checked": False,
        }
    }
    with patch("interface.internal.diagnostics.send_request", return_value=mock_payload):
        resp = client.get(
            "/internal/agents/diagnostics",
            headers={"X-Internal-Key": "very-secret-key"},
        )
    assert resp.status_code == 200
    assert resp.json() == mock_payload["response"]
