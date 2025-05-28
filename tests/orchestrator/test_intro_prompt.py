import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest

spec = importlib.util.spec_from_file_location(
    "legion.orchestrator"
    Path(__file__).resolve().parents[2] / "legion" / "orchestrator.py"
)
orch_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(orch_mod)
Orchestrator = orch_mod.Orchestrator


@pytest.fixture
def orch():
    return Orchestrator()


@pytest.mark.asyncio
async def test_intro_enqueued(monkeypatch, orch):
    queue_mock = MagicMock()
    monkeypatch.setattr(orch_mod, "task_queue", queue_mock)
    state_repo_mock = MagicMock()
    state_repo_mock.task_status.return_value = "success"
    monkeypatch.setattr(orch_mod, "state_repo", state_repo_mock)

    await orch.call_directive("echo.echo_task", new_thread=True)

    assert queue_mock.enqueue.call_count == 2
    intro_payload = queue_mock.enqueue.call_args_list[0][0][0].payload
    assert intro_payload["intro"] is True
