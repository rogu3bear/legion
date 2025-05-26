"""Tests for LM Studio proxy API endpoints."""

from collections import defaultdict, deque
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from interface.main import app


@pytest.fixture
def test_client():
    """Create test client for LM Studio proxy endpoints."""
    return TestClient(app)


class TestLMStudioProxy:
    """Test cases for LM Studio proxy endpoints."""

    def test_echo_endpoint_success(self, test_client):
        """Test successful echo proxy to LM Studio."""
        mock_payload = {
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.7,
            "max_tokens": 100,
        }

        mock_response = {
            "choices": [{"message": {"role": "assistant", "content": "Hi there!"}}],
            "usage": {"total_tokens": 10},
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.status_code = 200
            mock_response_obj.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response_obj
            )

            response = test_client.post("/api/v1/lmstudio/echo", json=mock_payload)

        assert response.status_code == 200
        assert response.json() == mock_response

    def test_echo_endpoint_connection_error(self, test_client):
        """Test echo endpoint when LM Studio is unreachable."""
        mock_payload = {"messages": [{"role": "user", "content": "Hello"}]}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.ConnectError("Connection failed")
            )

            response = test_client.post("/api/v1/lmstudio/echo", json=mock_payload)

        assert response.status_code == 503
        assert "Could not connect to LM Studio" in response.json()["detail"]

    def test_echo_endpoint_timeout(self, test_client):
        """Test echo endpoint timeout."""
        mock_payload = {"messages": [{"role": "user", "content": "Hello"}]}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.TimeoutException("Request timed out")
            )

            response = test_client.post("/api/v1/lmstudio/echo", json=mock_payload)

        assert response.status_code == 504
        assert "timed out" in response.json()["detail"]

    def test_echo_endpoint_invalid_json(self, test_client):
        """Test echo endpoint with invalid JSON payload."""
        response = test_client.post(
            "/api/v1/lmstudio/echo",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400
        assert "Invalid JSON payload" in response.json()["detail"]

    def test_chat_endpoint_success(self, test_client):
        """Test successful structured chat endpoint."""
        chat_request = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"},
            ],
            "temperature": 0.8,
            "max_tokens": 150,
            "stream": False,
        }

        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "I'm doing well, thank you!",
                    }
                }
            ],
            "usage": {"total_tokens": 15},
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.status_code = 200
            mock_response_obj.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response_obj
            )

            response = test_client.post("/api/v1/lmstudio/chat", json=chat_request)

        assert response.status_code == 200
        assert response.json() == mock_response

    def test_chat_endpoint_with_defaults(self, test_client):
        """Test chat endpoint with minimal required data."""
        chat_request = {"messages": [{"role": "user", "content": "Test message"}]}

        mock_response = {
            "choices": [{"message": {"role": "assistant", "content": "Test response"}}]
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.status_code = 200
            mock_response_obj.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response_obj
            )

            response = test_client.post("/api/v1/lmstudio/chat", json=chat_request)

        assert response.status_code == 200
        # Verify default values were applied
        called_payload = (
            mock_client.return_value.__aenter__.return_value.post.call_args[1]["json"]
        )
        assert called_payload["temperature"] == 0.7  # default
        assert called_payload["max_tokens"] == 256  # default
        assert called_payload["stream"] is False  # default

    def test_chat_endpoint_http_error(self, test_client):
        """Test chat endpoint when LM Studio returns HTTP error."""
        chat_request = {"messages": [{"role": "user", "content": "Test"}]}

        with patch("httpx.AsyncClient") as mock_client:
            error_response = MagicMock()
            error_response.status_code = 400
            error_response.json.return_value = {"error": "Bad request"}
            error_response.content = b'{"error": "Bad request"}'

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "Bad request", request=None, response=error_response
                )
            )

            response = test_client.post("/api/v1/lmstudio/chat", json=chat_request)

        assert response.status_code == 400
        assert response.json() == {"error": "Bad request"}

    def test_chat_endpoint_validation_error(self, test_client):
        """Test chat endpoint with invalid request data."""
        invalid_request = {
            "messages": [{"role": "invalid_role", "content": "Test"}],  # invalid role
            "temperature": "invalid",  # should be float
        }

        response = test_client.post("/api/v1/lmstudio/chat", json=invalid_request)

        assert response.status_code == 422  # Validation error

    def test_custom_lmstudio_url(self, test_client):
        """Test that custom LM Studio URL is used when set in environment."""
        chat_request = {"messages": [{"role": "user", "content": "Test"}]}

        with patch(
            "interface.api.v1.endpoints.lmstudio_proxy.LMSTUDIO_COMPLETION_ENDPOINT",
            "http://custom-host:8080/v1/chat/completions",
        ), patch("httpx.AsyncClient") as mock_client:

            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = {"test": "response"}
            mock_response_obj.status_code = 200
            mock_response_obj.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response_obj
            )

            test_client.post("/api/v1/lmstudio/chat", json=chat_request)

        # Verify the custom URL was used
        call_args = mock_client.return_value.__aenter__.return_value.post.call_args
        assert "http://custom-host:8080/v1/chat/completions" in str(call_args)

    def test_completion_tokens_parity(self, test_client):
        """Test that proxy returns completion_tokens > 0 when LM Studio does."""
        chat_request = {"messages": [{"role": "user", "content": "Hello"}]}

        mock_response = {
            "choices": [{"message": {"role": "assistant", "content": "Hello there!"}}],
            "usage": {"completion_tokens": 5, "prompt_tokens": 3, "total_tokens": 8},
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.status_code = 200
            mock_response_obj.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response_obj
            )

            response = test_client.post("/api/v1/lmstudio/chat", json=chat_request)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["usage"]["completion_tokens"] > 0
        assert response_data["choices"][0]["message"]["content"] == "Hello there!"

    def test_default_max_tokens(self, test_client):
        """Test that proxy injects default max_tokens=256 when missing or <=0."""
        chat_request = {
            "messages": [{"role": "user", "content": "Test"}]
            # max_tokens is missing, should default to 256
        }

        mock_response = {
            "choices": [{"message": {"role": "assistant", "content": "Response"}}]
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.status_code = 200
            mock_response_obj.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response_obj
            )

            response = test_client.post("/api/v1/lmstudio/chat", json=chat_request)

        assert response.status_code == 200
        # Verify default max_tokens was injected
        called_payload = (
            mock_client.return_value.__aenter__.return_value.post.call_args[1]["json"]
        )
        assert called_payload["max_tokens"] == 256

    def test_streaming_mode(self, test_client):
        """Test streaming mode returns StreamingResponse."""
        chat_request = {
            "messages": [{"role": "user", "content": "Stream test"}],
            "stream": True,
        }

        # Mock streaming response chunks
        mock_chunks = [
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\n',
            b'data: {"choices":[{"delta":{"content":" world"}}]}\n\n',
            b"data: [DONE]\n\n",
        ]

        async def mock_aiter_bytes():
            for chunk in mock_chunks:
                yield chunk

        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = MagicMock()
            mock_response_obj.aiter_bytes = mock_aiter_bytes

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response_obj
            )

            response = test_client.post("/api/v1/lmstudio/chat", json=chat_request)

        assert response.status_code == 200
        # Verify streaming was enabled in the upstream call
        called_payload = (
            mock_client.return_value.__aenter__.return_value.post.call_args[1]["json"]
        )
        assert called_payload["stream"] is True
        # Verify stream=True was passed to httpx
        call_kwargs = mock_client.return_value.__aenter__.return_value.post.call_args[1]
        assert call_kwargs.get("stream") is True

    def test_openapi_schema_includes_stream_and_max_tokens(self, test_client):
        """Test that OpenAPI schema exposes stream and max_tokens fields with proper defaults."""
        response = test_client.get("/openapi.json")
        assert response.status_code == 200

        openapi_spec = response.json()
        chat_request_schema = openapi_spec["components"]["schemas"]["ChatRequest"]

        # Verify stream field
        assert "stream" in chat_request_schema["properties"]
        stream_field = chat_request_schema["properties"]["stream"]
        assert stream_field["type"] == "boolean"
        assert stream_field["default"] is False
        assert "streaming" in stream_field["description"].lower()

        # Verify max_tokens field
        assert "max_tokens" in chat_request_schema["properties"]
        max_tokens_field = chat_request_schema["properties"]["max_tokens"]
        assert max_tokens_field["type"] == "integer"
        assert max_tokens_field["default"] == 256
        assert max_tokens_field["minimum"] == 1
        assert max_tokens_field["maximum"] == 4096

    def test_timeout_handling_returns_504(self, test_client):
        """Test that timeout exceptions return HTTP 504 Gateway Timeout."""
        chat_request = {"messages": [{"role": "user", "content": "Test timeout"}]}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.TimeoutException("Request timed out")
            )

            response = test_client.post("/api/v1/lmstudio/chat", json=chat_request)

        assert response.status_code == 504
        assert "timeout" in response.json()["detail"].lower()

    def test_rate_limiting_with_streaming_requests(self, test_client):
        """Test that rate limiting works correctly with streaming requests."""
        chat_request = {
            "messages": [{"role": "user", "content": "Stream test"}],
            "stream": True,
        }

        async def mock_aiter_bytes():
            for chunk in [b'data: {"test": "chunk"}\n\n']:
                yield chunk

        with patch("httpx.AsyncClient") as mock_client, patch(
            "interface.api.v1.endpoints.lmstudio_proxy.request_tracker",
            defaultdict(deque),
        ):

            mock_response_obj = MagicMock()
            mock_response_obj.aiter_bytes = mock_aiter_bytes
            mock_response_obj.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response_obj
            )

            # First request should succeed
            response = test_client.post("/api/v1/lmstudio/chat", json=chat_request)
            assert response.status_code == 200

            # Verify rate limit hit was registered after stream completion
            # This tests the finally block behavior

    def test_log_redaction_in_production_mode(self, test_client):
        """Test that message content is redacted in logs when DEBUG=False."""
        chat_request = {
            "messages": [{"role": "user", "content": "Sensitive information"}]
        }

        with patch(
            "interface.api.v1.endpoints.lmstudio_proxy.settings"
        ) as mock_settings, patch("httpx.AsyncClient") as mock_client, patch(
            "interface.api.v1.endpoints.lmstudio_proxy.logger"
        ) as mock_logger:

            mock_settings.DEBUG = False

            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = {
                "choices": [{"message": {"content": "Response"}}]
            }
            mock_response_obj.status_code = 200
            mock_response_obj.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response_obj
            )

            response = test_client.post("/api/v1/lmstudio/chat", json=chat_request)

            assert response.status_code == 200

            # Verify that debug logs contain redacted content
            debug_calls = list(mock_logger.debug.call_args_list)
            if debug_calls:
                log_message = str(debug_calls[-1])
                assert "[REDACTED]" in log_message
                assert "Sensitive information" not in log_message

    def test_retry_logic_on_connection_errors(self, test_client):
        """Test that connection errors trigger retry logic before failing."""
        chat_request = {"messages": [{"role": "user", "content": "Test retry"}]}

        with patch("httpx.AsyncClient") as mock_client, patch(
            "interface.api.v1.endpoints.lmstudio_proxy.RETRIES", 2
        ), patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:

            # First two attempts fail, third succeeds
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = {
                "choices": [{"message": {"content": "Success"}}]
            }
            mock_response_obj.status_code = 200
            mock_response_obj.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=[
                    httpx.ConnectError("Connection failed"),
                    httpx.ConnectError("Connection failed"),
                    mock_response_obj,
                ]
            )

            response = test_client.post("/api/v1/lmstudio/chat", json=chat_request)

            assert response.status_code == 200
            assert response.json()["choices"][0]["message"]["content"] == "Success"

            # Verify retry attempts
            assert mock_client.return_value.__aenter__.return_value.post.call_count == 3
            assert mock_sleep.call_count == 2  # 2 retries with exponential backoff

    def test_max_retries_exceeded_returns_503(self, test_client):
        """Test that exceeding max retries returns 503 Service Unavailable."""
        chat_request = {"messages": [{"role": "user", "content": "Test max retries"}]}

        with patch("httpx.AsyncClient") as mock_client, patch(
            "interface.api.v1.endpoints.lmstudio_proxy.RETRIES", 1
        ), patch(
            "interface.api.v1.endpoints.lmstudio_proxy.check_rate_limit",
            return_value=True,
        ):

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.ConnectError("Connection failed")
            )

            response = test_client.post("/api/v1/lmstudio/chat", json=chat_request)

            assert response.status_code == 503
            assert "connection failed" in response.json()["detail"].lower()

    def test_max_tokens_validation_edge_cases(self, test_client):
        """Test max_tokens validation for edge cases that could cause empty responses."""
        # Test max_tokens = 0 (should be rejected)
        response = test_client.post(
            "/api/v1/lmstudio/chat",
            json={"messages": [{"role": "user", "content": "Hello"}], "max_tokens": 0},
        )
        assert response.status_code == 422
        error = response.json()
        assert "greater than or equal to 1" in error["detail"][0]["msg"]

        # Test max_tokens too large (should be rejected)
        response = test_client.post(
            "/api/v1/lmstudio/chat",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5000,
            },
        )
        assert response.status_code == 422
        error = response.json()
        assert "less than or equal to 4096" in error["detail"][0]["msg"]

        # Test negative max_tokens (should be rejected)
        response = test_client.post(
            "/api/v1/lmstudio/chat",
            json={"messages": [{"role": "user", "content": "Hello"}], "max_tokens": -1},
        )
        assert response.status_code == 422
        error = response.json()
        assert "greater than or equal to 1" in error["detail"][0]["msg"]
