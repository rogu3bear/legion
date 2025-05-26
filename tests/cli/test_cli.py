import json
import sys
from unittest.mock import MagicMock

import pytest

import legion.cli as cli
from legion.orchestrator import AgentLoadError


class FakeOrchestrator:
    def __init__(self, *args, **kwargs):  # accept any params from cli.main()
        # Simulate loaded config
        self.config = {
            "architect": {"class": "ArchitectAgent"},
            "echo": {"class": "EchoAgent"},
        }
        # Simulate port allocations
        self.port_allocator = MagicMock()
        self.port_allocator._allocations = {"architect": 7000, "echo": 7001}
        self.port_allocator.get_all_resolved_ports = (
            lambda: self.port_allocator._allocations
        )

    def load_agent(self, key):
        if key not in self.config:
            raise AgentLoadError(f"Unknown agent key {key}")
        return object()

    def dispatch(self, key, payload):
        return {"status": "ok", "echo": payload}


@pytest.fixture(autouse=True)
def mock_orchestrator(monkeypatch):
    monkeypatch.setattr(cli, "Orchestrator", FakeOrchestrator)
    return FakeOrchestrator


def test_list_agents(capsys):
    with pytest.raises(SystemExit) as exc:
        sys.argv = ["legion", "list-agents"]
        cli.main()
    code = exc.value.code
    captured = capsys.readouterr()
    assert code == 0
    lines = captured.out.strip().splitlines()
    assert "architect\tArchitectAgent" in lines
    assert "echo\tEchoAgent" in lines


@pytest.mark.parametrize(
    "key,msg",
    [
        ("architect", None),
        ("echo", "hello"),
    ],
)
def test_run_agent_success(capsys, key, msg):
    args = ["run-agent", key] + (["-m", msg] if msg else [])
    with pytest.raises(SystemExit) as exc:
        sys.argv = ["legion", *args]
        cli.main()
    code = exc.value.code
    output = capsys.readouterr().out
    assert code == 0
    data = json.loads(output)
    assert data["status"] == "ok"
    assert data["echo"] == {"message": msg or "ping"}


def test_run_agent_unknown(capsys):
    with pytest.raises(SystemExit) as exc:
        sys.argv = ["legion", "run-agent", "badkey"]
        cli.main()
    code = exc.value.code
    err = capsys.readouterr().err
    assert code == 3
    assert "Error loading agent badkey" in err


def test_show_config(capsys):
    with pytest.raises(SystemExit) as exc:
        sys.argv = ["legion", "show-config"]
        cli.main()
    code = exc.value.code
    out = capsys.readouterr().out
    assert code == 0
    conf = json.loads(out)
    assert "architect" in conf and "echo" in conf


def test_ports(capsys):
    # Ensure port allocations
    with pytest.raises(SystemExit) as exc:
        sys.argv = ["legion", "ports"]
        cli.main()
    code = exc.value.code
    out_lines = capsys.readouterr().out.strip().splitlines()
    assert code == 0
    assert "architect\t7000" in out_lines
    assert "echo\t7001" in out_lines


def test_version(capsys, monkeypatch):
    # Monkeypatch version and git
    monkeypatch.setattr(cli, "version", lambda pkg: "1.2.3")
    monkeypatch.setattr(
        cli.subprocess, "check_output", lambda *args, **kwargs: b"abcdef\n"
    )
    with pytest.raises(SystemExit) as exc:
        sys.argv = ["legion", "version"]
        cli.main()
    code = exc.value.code
    out = capsys.readouterr().out.strip()
    assert code == 0
    assert out == "1.2.3+abcdef"
