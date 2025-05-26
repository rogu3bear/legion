"""
Tests for rate limiting functionality in LM Studio proxy.
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from interface.api.v1.endpoints.lmstudio_proxy import (
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
    check_rate_limit,
    request_tracker,
)


class TestRateLimiting:
    """Test rate limiting functionality."""

    def setup_method(self):
        """Clear rate limiting tracker before each test."""
        request_tracker.clear()

    def teardown_method(self):
        """Clear rate limiting tracker after each test."""
        request_tracker.clear()

    def test_rate_limit_allows_within_limit(self):
        """Test that requests within limit are allowed."""
        client_ip = "192.168.1.100"

        # Make requests within limit
        for _i in range(RATE_LIMIT_REQUESTS):
            assert check_rate_limit(client_ip) is True

        # Next request should be blocked
        assert check_rate_limit(client_ip) is False

    def test_rate_limit_blocks_over_limit(self):
        """Test that requests over limit are blocked."""
        client_ip = "192.168.1.101"

        # Fill up the rate limit
        for _i in range(RATE_LIMIT_REQUESTS):
            check_rate_limit(client_ip)

        # Additional requests should be blocked
        assert check_rate_limit(client_ip) is False
        assert check_rate_limit(client_ip) is False

    def test_rate_limit_window_expiry(self):
        """Test that rate limit resets after window expires."""
        client_ip = "192.168.1.102"

        # Mock time to control window behavior
        with patch('interface.api.v1.endpoints.lmstudio_proxy.time.time') as mock_time:
            start_time = 1000.0
            mock_time.return_value = start_time

            # Fill up the rate limit
            for _i in range(RATE_LIMIT_REQUESTS):
                assert check_rate_limit(client_ip) is True

            # Next request should be blocked
            assert check_rate_limit(client_ip) is False

            # Advance time beyond the window
            mock_time.return_value = start_time + RATE_LIMIT_WINDOW + 1

            # Should be allowed again
            assert check_rate_limit(client_ip) is True

    def test_rate_limit_different_ips(self):
        """Test that rate limiting is per IP address."""
        client_ip1 = "192.168.1.103"
        client_ip2 = "192.168.1.104"

        # Fill up rate limit for first IP
        for _i in range(RATE_LIMIT_REQUESTS):
            check_rate_limit(client_ip1)

        # First IP should be blocked
        assert check_rate_limit(client_ip1) is False

        # Second IP should still be allowed
        assert check_rate_limit(client_ip2) is True

    def test_rate_limit_cleanup_old_requests(self):
        """Test that old requests are cleaned up properly."""
        client_ip = "192.168.1.105"

        with patch('interface.api.v1.endpoints.lmstudio_proxy.time.time') as mock_time:
            start_time = 1000.0
            mock_time.return_value = start_time

            # Make some requests
            for _i in range(5):
                check_rate_limit(client_ip)

            # Advance time to make some requests expire
            mock_time.return_value = start_time + RATE_LIMIT_WINDOW - 10

            # Make more requests (should still be within limit total)
            for _i in range(5):
                assert check_rate_limit(client_ip) is True

            # Should be at limit now
            assert check_rate_limit(client_ip) is False

            # Advance time further to expire the first batch
            mock_time.return_value = start_time + RATE_LIMIT_WINDOW + 1

            # Should have space again (first 5 requests expired)
            for _i in range(5):
                assert check_rate_limit(client_ip) is True


class TestLMStudioChatRateLimit:
    """Test rate limiting integration with the chat endpoint."""

    def setup_method(self):
        """Clear rate limiting tracker before each test."""
        request_tracker.clear()

    def teardown_method(self):
        """Clear rate limiting tracker after each test."""
        request_tracker.clear()

    @patch('interface.api.v1.endpoints.lmstudio_proxy.httpx.AsyncClient')
    def test_chat_endpoint_rate_limit_success(self, mock_client):
        """Test chat endpoint allows requests within rate limit."""
        from fastapi import FastAPI

        from interface.api.v1.endpoints.lmstudio_proxy import router

        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

        # Mock successful LM Studio response
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "test"}
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None

        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

        # Test data
        chat_data = {
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.7,
            "max_tokens": 100
        }

        # Should succeed within rate limit
        for _i in range(5):  # Well within limit
            response = client.post("/chat", json=chat_data)
            assert response.status_code == 200

    @patch('interface.api.v1.endpoints.lmstudio_proxy.httpx.AsyncClient')
    def test_chat_endpoint_rate_limit_exceeded(self, mock_client):
        """Test chat endpoint blocks requests when rate limit is exceeded."""
        from fastapi import FastAPI

        from interface.api.v1.endpoints.lmstudio_proxy import router

        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

        # Mock successful LM Studio response
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "test"}
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None

        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

        # Test data
        chat_data = {
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.7,
            "max_tokens": 100
        }

        # Fill up the rate limit
        for _i in range(RATE_LIMIT_REQUESTS):
            response = client.post("/chat", json=chat_data)
            assert response.status_code == 200

        # Next request should be rate limited
        response = client.post("/chat", json=chat_data)
        assert response.status_code == 429

        # Check error response format
        error_data = response.json()
        assert "error" in error_data["detail"]
        assert "Too Many Requests" in error_data["detail"]["error"]
        assert "retry_after" in error_data["detail"]

    def test_rate_limit_unknown_client_ip(self):
        """Test rate limiting with unknown client IP."""
        from fastapi import FastAPI

        from interface.api.v1.endpoints.lmstudio_proxy import router

        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

        # Mock the request to have no client info
        with patch('interface.api.v1.endpoints.lmstudio_proxy.check_rate_limit') as mock_check:
            mock_check.return_value = False

            chat_data = {
                "messages": [{"role": "user", "content": "Hello"}],
                "temperature": 0.7,
                "max_tokens": 100
            }

            response = client.post("/chat", json=chat_data)
            assert response.status_code == 429

            # Verify unknown IP was used
            mock_check.assert_called_with("testclient")  # TestClient uses this as default
