"""Tests for HTTPClient wrapper"""

import os

# Ensure src directory is on PYTHONPATH for common imports
import sys

import pytest
import requests

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from common.http_client import HTTPClient


class DummyResp:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


@pytest.fixture(autouse=True)
def env_vars(monkeypatch):
    monkeypatch.setenv("MIDDLEWARE_URL", "http://test")
    monkeypatch.setenv("HTTP_CLIENT_MAX_RETRIES", "2")
    monkeypatch.setenv("HTTP_CLIENT_BACKOFF", "0.1")
    monkeypatch.setenv("AGENT_NAME", "test_agent")
    yield


@pytest.fixture
def dummy_session(monkeypatch):
    class Session:
        def post(self, url, json, headers, timeout):
            assert url.startswith("http://test")
            assert headers.get("X-Agent-Name") == "test_agent"
            return DummyResp({"ok": True})

        def get(self, url, headers, timeout):
            assert headers.get("X-Agent-Name") == "test_agent"
            return DummyResp({"ok": True})

    monkeypatch.setattr(requests, "Session", Session)


def test_http_post(dummy_session):
    client = HTTPClient()
    resp = client.post("/path", json={"a": 1})
    assert resp == {"ok": True}


def test_http_get(dummy_session):
    client = HTTPClient()
    resp = client.get("/path")
    assert resp == {"ok": True}
