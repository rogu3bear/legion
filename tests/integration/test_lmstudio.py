"""Integration tests for LM Studio MCP Bridge."""

import os
from unittest.mock import AsyncMock, patch

import pytest

from legion.core.llm_mode_client import ModeSwitchingLLMClient
from legion.mcp.bridges.lmstudio_bridge import LMStudioAdapter, LMStudioMCP


@pytest.fixture
def lmstudio_available():
    """Check if LM Studio is available on the default port."""
    try:
        import httpx
        with httpx.Client() as client:
            response = client.get("http://127.0.0.1:1234/v1/models", timeout=2.0)
            return response.status_code == 200
    except Exception:
        return False


@pytest.mark.asyncio
async def test_lmstudio_adapter_init():
    """Test LM Studio adapter initialization."""
    adapter = LMStudioAdapter()
    assert adapter.base_url.endswith("/v1")
    assert adapter.completions_endpoint.endswith("/chat/completions")
    assert adapter.models_endpoint.endswith("/models")


@pytest.mark.asyncio
async def test_lmstudio_adapter_discover_models_mock():
    """Test model discovery with mocked response."""
    adapter = LMStudioAdapter()

    mock_response = {
        "data": [
            {"id": "meta-llama-3.1-8b-instruct", "object": "model"},
            {"id": "gpt-4", "object": "model"}
        ]
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=AsyncMock(
                status_code=200,
                json=lambda: mock_response,
                raise_for_status=lambda: None
            )
        )

        result = await adapter.discover_model()
        assert "data" in result
        assert len(result["data"]) == 2


@pytest.mark.asyncio
async def test_lmstudio_adapter_chat_complete_mock():
    """Test chat completion with mocked response."""
    adapter = LMStudioAdapter()

    mock_response = {
        "choices": [
            {
                "message": {
                    "content": "Hello! How can I help you today?"
                }
            }
        ]
    }

    messages = [{"role": "user", "content": "Hello"}]

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=AsyncMock(
                status_code=200,
                json=lambda: mock_response,
                raise_for_status=lambda: None
            )
        )

        result = await adapter.chat_complete(messages)
        assert "choices" in result
        assert result["choices"][0]["message"]["content"] == "Hello! How can I help you today?"


@pytest.mark.asyncio
async def test_lmstudio_adapter_stats_healthy():
    """Test stats method when service is healthy."""
    adapter = LMStudioAdapter()

    mock_models_response = {"data": [{"id": "test-model"}]}

    with patch.object(adapter, "discover_model", return_value=mock_models_response):
        stats = await adapter.stats()
        assert stats["status"] == "healthy"
        assert stats["models_available"] == 1
        assert "base_url" in stats


@pytest.mark.asyncio
async def test_lmstudio_adapter_stats_unhealthy():
    """Test stats method when service is unhealthy."""
    adapter = LMStudioAdapter()

    with patch.object(adapter, "discover_model", side_effect=Exception("Connection failed")):
        stats = await adapter.stats()
        assert stats["status"] == "unhealthy"
        assert "error" in stats


def test_lmstudio_mcp_init():
    """Test LM Studio MCP server initialization."""
    mcp = LMStudioMCP()
    assert mcp.adapter is not None
    assert mcp.app is not None
    assert mcp.app.title == "LM Studio MCP Bridge"


@pytest.mark.asyncio
async def test_mode_switching_client_local_mode():
    """Test mode-switching client in local mode."""
    with patch.dict(os.environ, {"LLM_MODE": "local"}):
        client = ModeSwitchingLLMClient()
        assert client.mode == "local"
        assert hasattr(client, "lmstudio_adapter")


@pytest.mark.asyncio
async def test_mode_switching_client_remote_mode():
    """Test mode-switching client in remote mode."""
    with patch.dict(os.environ, {"LLM_MODE": "remote"}):
        client = ModeSwitchingLLMClient()
        assert client.mode == "remote"
        assert hasattr(client, "openai")


@pytest.mark.asyncio
async def test_mode_switching_client_call_local():
    """Test mode-switching client call in local mode."""
    with patch.dict(os.environ, {"LLM_MODE": "local"}):
        client = ModeSwitchingLLMClient()

        mock_response = {
            "choices": [{"message": {"content": "Test response"}}]
        }

        with patch.object(client.lmstudio_adapter, "chat_complete", return_value=mock_response):
            messages = [{"role": "user", "content": "test"}]
            result = await client.call(messages)
            assert result == "Test response"


@pytest.mark.asyncio
@pytest.mark.skipif(not pytest.importorskip("httpx"), reason="httpx not available")
async def test_lmstudio_adapter_real_connection(lmstudio_available):
    """Test real connection to LM Studio if available."""
    if not lmstudio_available:
        pytest.skip("LM Studio not available on port 1234")

    adapter = LMStudioAdapter()

    # Test model discovery
    models = await adapter.discover_model()
    assert "data" in models or "error" in models

    # Test health check
    stats = await adapter.stats()
    assert "status" in stats


@pytest.mark.asyncio
async def test_mode_switching_client_health_check_local():
    """Test health check in local mode."""
    with patch.dict(os.environ, {"LLM_MODE": "local"}):
        client = ModeSwitchingLLMClient()

        mock_stats = {"status": "healthy", "models_available": 1}

        with patch.object(client.lmstudio_adapter, "stats", return_value=mock_stats):
            health = await client.health_check()
            assert health["status"] == "healthy"


@pytest.mark.asyncio
async def test_mode_switching_client_generate_legacy():
    """Test legacy generate method for backward compatibility."""
    with patch.dict(os.environ, {"LLM_MODE": "local"}):
        client = ModeSwitchingLLMClient()

        mock_response = {
            "choices": [{"message": {"content": "Legacy response"}}]
        }

        with patch.object(client.lmstudio_adapter, "chat_complete", return_value=mock_response):
            result = client.generate(
                agent_name="test",
                thread_id="default",
                dynamic_rules={"default": [{"role": "system", "content": "You are helpful"}]},
                history=[{"role": "user", "content": "test"}]
            )
            assert result == "Legacy response"
