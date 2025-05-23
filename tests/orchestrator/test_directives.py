import importlib
from pathlib import Path
from unittest.mock import MagicMock

import pytest

spec = importlib.util.spec_from_file_location("legion.orchestrator.directives", Path(__file__).resolve().parents[2]/"legion"/"orchestrator"/"directives.py")

directives = importlib.util.module_from_spec(spec)
spec.loader.exec_module(directives)


@pytest.fixture(autouse=True)
def clear_threads():
    directives._KNOWN_THREADS.clear()


def test_process_directive_new_thread(monkeypatch):
    q = MagicMock()
    monkeypatch.setattr(directives, "queue", q)

    payload = {"agent": "echo", "directive": "echo.echo_task", "thread_id": "t1"}
    task_id = directives.process_directive(payload)

    q.enqueue.assert_called_once()
    task = q.enqueue.call_args[0][0]
    assert task.agent == "echo"
    assert task.payload["intro"] is True
    assert task.id == task_id
    assert "t1" in directives._KNOWN_THREADS


def test_process_directive_existing_thread(monkeypatch):
    q = MagicMock()
    monkeypatch.setattr(directives, "queue", q)

    first = {"agent": "echo", "directive": "echo.echo_task", "thread_id": "t1"}
    directives.process_directive(first)
    q.enqueue.reset_mock()

    second = {"agent": "echo", "directive": "echo.echo_task", "thread_id": "t1"}
    directives.process_directive(second)

    task = q.enqueue.call_args[0][0]
    assert task.payload["intro"] is False
