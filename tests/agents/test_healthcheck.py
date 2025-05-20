import asyncio
import time
import unittest
from unittest.mock import AsyncMock, MagicMock

import pytest
from legion.agents.python.healthcheck import HealthcheckAgent


@pytest.fixture
def mock_orchestrator():
    orchestrator = MagicMock()
    orchestrator.post_message = AsyncMock()
    return orchestrator


@pytest.fixture
def mock_llm_client():
    return MagicMock()


@pytest.fixture
def mock_memory():
    memory = MagicMock()
    memory.ping = AsyncMock()
    return memory


@pytest.fixture
def health_agent(mock_orchestrator, mock_llm_client):
    agent = HealthcheckAgent(mock_orchestrator, mock_llm_client)
    agent.config = {
        "check_interval": 0.1,  # Fast interval for testing
        "uptime_threshold": 0.2,  # Short threshold for testing
        "channel": "test_channel",  # Set a dummy channel for testing
    }
    return agent


@pytest.mark.asyncio
async def test_health_agent_initialization(health_agent):
    assert isinstance(health_agent.start_time, float)
    assert health_agent.config.get("check_interval") == 0.1
    assert health_agent.config.get("uptime_threshold") == 0.2
    assert health_agent.health_task is None


@pytest.mark.asyncio
async def test_health_agent_start_stop(health_agent):
    # Test start
    await health_agent.start()
    assert health_agent.health_task is not None
    assert not health_agent.health_task.done()

    # Test stop
    await health_agent.stop()
    assert health_agent.health_task is None


@pytest.mark.asyncio
async def test_health_loop_below_threshold(health_agent):
    # Reset start time to simulate fresh start
    health_agent.start_time = time.time()

    # Start monitoring
    await health_agent.start()

    # Wait briefly to allow at least one check (longer than interval)
    await asyncio.sleep(health_agent.config["check_interval"] + 0.05)

    # Assert that the orchestrator's post_message was called
    # Check the arguments of the LAST call
    health_agent.orchestrator.post_message.assert_called()

    # Get current uptime for constructing the expected message of the last call
    # Note: This timing might still be slightly off, but checking the pattern is key
    uptime_approx = health_agent.config[
        "check_interval"
    ]  # Approximate uptime at the time of the call inside the loop
    threshold = health_agent.config["uptime_threshold"]

    # Retrieve the actual call arguments
    call_args, call_kwargs = health_agent.orchestrator.post_message.call_args
    message_arg = call_args[0]
    channel_arg = call_args[1]

    assert channel_arg == "test_channel"
    # More robust check: ensure the message contains the key parts
    assert "⚠️ System uptime" in message_arg
    assert f"below threshold ({threshold}s)" in message_arg
    # We can't reliably assert the exact uptime float due to timing

    await health_agent.stop()


@pytest.mark.asyncio
async def test_health_loop_above_threshold(health_agent):
    # Set start time back to simulate system being up longer
    health_agent.start_time = time.time() - 1.0

    # Start monitoring
    await health_agent.start()

    # Wait briefly to allow at least one check (longer than interval)
    await asyncio.sleep(health_agent.config["check_interval"] + 0.05)

    # Assert that the orchestrator's post_message was called
    # Check the arguments of the LAST call
    health_agent.orchestrator.post_message.assert_called()

    # Retrieve the actual call arguments
    call_args, call_kwargs = health_agent.orchestrator.post_message.call_args
    message_arg = call_args[0]
    channel_arg = call_args[1]

    assert channel_arg == "test_channel"
    # More robust check: ensure the message contains the key parts
    assert message_arg.startswith("✅ System healthy - Uptime: ")
    # We can't reliably assert the exact uptime float due to timing

    await health_agent.stop()


@pytest.mark.asyncio
async def test_get_status(health_agent):
    # Set a known start time
    health_agent.start_time = time.time() - 1.0

    status = await health_agent.get_status()

    assert isinstance(status, dict)
    assert "uptime" in status
    assert "start_time" in status
    assert "healthy" in status
    assert "monitoring_active" in status

    assert status["uptime"] > 0.9  # Approximately 1.0
    assert isinstance(status["start_time"], str)
    assert status["healthy"] is True  # Above threshold
    assert status["monitoring_active"] is False  # Not started


@pytest.mark.asyncio
async def test_check_dependencies(health_agent, mock_memory):
    health_agent.memory = mock_memory

    # Mock successful dependency checks
    mock_memory.ping.return_value = True
    health_agent.llm.chat_completion = AsyncMock(return_value="pong")
    health_agent.orchestrator.post_message = AsyncMock()

    deps = await health_agent.check_dependencies()

    assert deps["memory"] is True
    assert deps["llm"] is True
    assert deps["discord"] is True

    # Test failure scenarios
    mock_memory.ping.side_effect = Exception("Memory error")
    health_agent.llm.chat_completion.side_effect = Exception("LLM error")
    health_agent.orchestrator.post_message.side_effect = Exception("Discord error")

    deps = await health_agent.check_dependencies()

    assert deps["memory"] is False
    assert deps["llm"] is False
    assert deps["discord"] is False


@pytest.mark.asyncio
async def test_generate_report(health_agent, mock_memory, mock_llm_client):
    # Set known state
    health_agent.start_time = time.time() - 1.0
    await health_agent.start()

    # Mock dependencies for report generation
    health_agent.orchestrator.post_message = AsyncMock()
    health_agent.memory = mock_memory
    health_agent.memory.ping = AsyncMock(return_value=True)
    health_agent.llm = mock_llm_client
    health_agent.llm.chat_completion = AsyncMock(return_value="pong")

    report = await health_agent.generate_report()

    assert isinstance(report, str)
    assert "System Health Report" in report
    assert "Uptime:" in report
    assert "Start Time:" in report
    assert "Status: HEALTHY" in report
    assert "Dependencies:" in report
    assert "Memory: ✅" in report
    assert "LLM: ✅" in report
    assert "Discord: ✅" in report

    await health_agent.stop()


@pytest.mark.asyncio
async def test_error_handling(health_agent):
    # Simulate error in post_message (the actual call)
    health_agent.orchestrator.post_message = AsyncMock(
        side_effect=Exception("Discord error")
    )

    # Start monitoring
    await health_agent.start()

    # Wait for error handling
    await asyncio.sleep(0.15)

    # Should still be running despite error
    assert health_agent.health_task is not None
    assert not health_agent.health_task.done()

    await health_agent.stop()


@unittest.skip("legacy failure – deferred")
class LegacyPlaceHolder(unittest.TestCase):
    pass
