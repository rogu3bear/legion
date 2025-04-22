import os
import sys

import pytest

from legion.orchestrator import Orchestrator


def test_orchestrator_duplicate_lock(tmp_path, monkeypatch):
    pid_path = tmp_path / "orch.pid"
    # Patch os.kill to simulate that the fake PID is alive
    monkeypatch.setattr(os, "kill", lambda pid, sig: None)

    # Patch sys.exit to raise for test
    class ExitCalled(Exception):
        pass

    monkeypatch.setattr(sys, "exit", lambda code=1: (_ for _ in ()).throw(ExitCalled()))
    # First instance should succeed
    orch1 = Orchestrator(pid_file=str(pid_path))
    assert pid_path.exists()
    # Write a fake PID to simulate a running process
    with open(pid_path, "w") as f:
        f.write("12345")
    # Patch os.getpid to return a different value for the second instance
    monkeypatch.setattr(os, "getpid", lambda: 67890)
    # Second instance should exit
    with pytest.raises(ExitCalled):
        Orchestrator(pid_file=str(pid_path))
    # PID file should still contain the fake PID
    with open(pid_path, "r") as f:
        assert f.read().strip() == "12345"
    # Release lock and check file is removed
    orch1._release_lock()
    assert not pid_path.exists()
