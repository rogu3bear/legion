import asyncio
import importlib.util
import string
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Load orchestrator module from file path to avoid package clashes
spec = importlib.util.spec_from_file_location(
    "legion.orchestrator",
    Path(__file__).resolve().parents[2] / "legion" / "orchestrator.py",
)
orch_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(orch_mod)
Orchestrator = orch_mod.Orchestrator


@pytest.fixture
def orch():
    return Orchestrator()


def test_send_to_therapist_success(monkeypatch, orch):
    bus = MagicMock()
    monkeypatch.setattr(orch, "bus", bus)
    state_repo_mock = MagicMock()
    monkeypatch.setattr(orch_mod, "state_repo", state_repo_mock)

    req_id = orch.send_to_therapist("task1", {"foo": "bar"})

    assert isinstance(req_id, str)
    assert len(req_id) == 32
    assert all(c in string.hexdigits for c in req_id)
    bus.publish.assert_called_once()
    state_repo_mock.log_therapist_req.assert_called_once()


@pytest.mark.asyncio
async def test_receive_from_therapist_timeout(monkeypatch, orch):
    async def empty_async_iter():
        if False:
            yield None

    bus = MagicMock()
    bus.subscribe.return_value = empty_async_iter()
    monkeypatch.setattr(orch, "bus", bus)

    with pytest.raises(TimeoutError):
        await orch.receive_from_therapist({"id": "foo"})


def test_agent_comm_router_valid_target(monkeypatch, orch):
    bus = MagicMock()
    monkeypatch.setattr(orch, "bus", bus)
    monkeypatch.setattr(
        orch_mod,
        "agent_registry",
        {"echo": {"channel_in": "agent.echo.in"}},
    )

    orch.agent_comm_router({"target": "echo", "payload": "hi"})

    bus.publish.assert_called_once_with("agent.echo.in", {"payload": "hi"})


@pytest.mark.asyncio
async def test_call_directive_lifecycle(monkeypatch, orch):
    queue_mock = MagicMock()
    monkeypatch.setattr(orch_mod, "task_queue", queue_mock)
    state_repo_mock = MagicMock()
    state_repo_mock.task_status.side_effect = ["queued", "success"]
    monkeypatch.setattr(orch_mod, "state_repo", state_repo_mock)

    await orch.call_directive("echo.echo_task", foo=1)

    queue_mock.enqueue.assert_called_once()
    assert state_repo_mock.task_status.call_count >= 2
