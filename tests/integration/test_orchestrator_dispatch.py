"""Integration tests for the Orchestrator dispatch message flow."""

import pytest
import json
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from legion.orchestrator import Orchestrator
from legion.core.state import StateManager
from legion.agents.python import EchoAgent
from legion.core.di_container import container, ILLMClient, IStateManager

# Mock LLM Client
class MockLLMClient:
    async def call(self, messages: list, **kwargs) -> str:
        return "Mock LLM Response"
    def get_embedding(self, text: str) -> list[float]:
        return [0.1] * 1536

@pytest.fixture
def test_env(tmp_path):
    """Provides a temporary environment with isolated state directory."""
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    # Mock the default StateManager to use the temp dir
    original_state_manager = container.get(IStateManager)
    container.register_instance(IStateManager, StateManager(state_dir=str(state_dir)))
    # Mock the LLM Client
    original_llm_client = container.get(ILLMClient)
    container.register_instance(ILLMClient, MockLLMClient())
    yield {
        "state_dir": state_dir,
        "state_manager": container.get(IStateManager)
    }
    # Restore original container state
    container.register_instance(IStateManager, original_state_manager)
    container.register_instance(ILLMClient, original_llm_client)

@pytest.mark.asyncio
async def test_dispatch_message_integration(test_env, monkeypatch):
    """Tests the orchestrator dispatch flow, including state logging and telemetry."""
    state_manager = test_env["state_manager"]
    # Ensure EchoAgent is available for testing
    if "echo_agent" not in Orchestrator.CLASS_MAP:
        Orchestrator.CLASS_MAP["echo_agent"] = EchoAgent
    
    # Mock post_to_discord to prevent actual Discord calls
    mock_post = AsyncMock()
    monkeypatch.setattr(EchoAgent, "post_to_discord", mock_post, raising=False)

    # Instantiate orchestrator (uses mocked services via DI container)
    orchestrator = Orchestrator()

    # Dispatch a message to the EchoAgent
    agent_name = "echo_agent"
    content = "hello integration test"
    author = "pytest"
    timestamp = time.time()

    reply = await orchestrator.dispatch_message(
        agent_name=agent_name,
        content=content,
        author=author,
        timestamp=str(timestamp)
    )

    # 1. Assert correct reply from EchoAgent
    assert reply == f"Echoing: {content}"

    # 2. Assert Discord post was called (or attempted)
    mock_post.assert_called_once()

    # 3. Assert StateManager logs contain expected events
    log_file = test_env["state_dir"] / "tasks.jsonl"
    assert log_file.exists()
    log_entries = []
    with open(log_file, "r") as f:
        for line in f:
            log_entries.append(json.loads(line))
    
    assert len(log_entries) >= 4 # dispatch, validated, response, telemetry

    event_types = [entry["type"] for entry in log_entries]
    assert "dispatch" in event_types
    assert "validated" in event_types
    assert "response" in event_types
    assert "llm_latency" in event_types # EchoAgent doesn't call LLM, but handle_message might log 0
    assert "dispatch_duration" in event_types

    # Check dispatch event details
    dispatch_event = next(e for e in log_entries if e["type"] == "dispatch")
    assert dispatch_event["agent"] == agent_name
    assert dispatch_event["content"] == content
    assert dispatch_event["author"] == author

    # Check response event details
    response_event = next(e for e in log_entries if e["type"] == "response")
    assert response_event["agent"] == agent_name
    assert response_event["response"] == reply

    # Check telemetry events
    duration_event = next(e for e in log_entries if e["type"] == "dispatch_duration")
    assert duration_event["agent"] == agent_name
    assert duration_event["latency"] > 0
    assert duration_event["event"] == "dispatch_message" 