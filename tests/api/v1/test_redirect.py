"""Tests for legacy URL redirect functionality."""

import pytest
from fastapi.testclient import TestClient

from interface.main import app


class TestLegacyRedirects:
    """Test cases for legacy URL redirects."""

    def test_nexus_root_redirect(self):
        """Test that /nexus redirects to /log with 301 status."""
        client = TestClient(app)
        response = client.get("/nexus", follow_redirects=False)
        
        assert response.status_code == 301
        assert response.headers["location"] == "/log"

    def test_nexus_path_redirect(self):
        """Test that /nexus/subpath redirects to /log/subpath with 301 status."""
        client = TestClient(app)
        response = client.get("/nexus/search", follow_redirects=False)
        
        assert response.status_code == 301
        assert response.headers["location"] == "/log/search"

    def test_nexus_deep_path_redirect(self):
        """Test that nested /nexus/ paths redirect correctly."""
        client = TestClient(app)
        response = client.get("/nexus/api/v1/events", follow_redirects=False)
        
        assert response.status_code == 301
        assert response.headers["location"] == "/log/api/v1/events"

    def test_nexus_query_params_redirect(self):
        """Test that query parameters are not preserved in redirect (by design)."""
        client = TestClient(app)
        response = client.get("/nexus/search?q=test&limit=10", follow_redirects=False)
        
        assert response.status_code == 301
        assert response.headers["location"] == "/log/search"

    def test_redirect_follow_through(self):
        """Test that following redirects works end-to-end."""
        client = TestClient(app)
        # This will follow the redirect and should hit the /log endpoint (if it exists)
        # Since /log doesn't exist yet, it will return 404, but the redirect should work
        response = client.get("/nexus", follow_redirects=True)
        
        # We expect 404 since /log endpoint doesn't exist yet, but redirect should work
        assert response.status_code == 404
        # The final URL should be /log
        assert "/log" in str(response.url) 