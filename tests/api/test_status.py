from fastapi.testclient import TestClient
from interface.main import app
from unittest.mock import patch

client = TestClient(app)


def test_status_ok():
    payload = {"response": {"uptime": 42.0, "active_agents": ["a1", "a2"]}}
    with patch("interface.main.send_request", return_value=payload):
        resp = client.get("/status")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "uptime": 42.0, "agents": ["a1", "a2"]}


def test_status_unavailable():
    with patch("interface.main.send_request", return_value=None):
        resp = client.get("/status")
    assert resp.status_code == 503
