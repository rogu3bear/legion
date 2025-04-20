import os
import sys
import tempfile
import shutil
import pytest
from legion.orchestrator import Orchestrator

def test_agent_channel_ids_not_empty():
    from legion.orchestrator import Orchestrator
    orchestrator = Orchestrator()
    assert orchestrator.agent_channel_ids, "agent_channel_ids should not be empty after startup"

def test_duplicate_startup_and_cleanup(monkeypatch, caplog):
    # Use a temp PID file location
    tmp_pid = tempfile.NamedTemporaryFile(delete=False)
    tmp_pid.close()
    pid_path = tmp_pid.name
    # Patch sys.exit to raise a custom exception
    class ExitCalled(Exception): pass
    monkeypatch.setattr(sys, 'exit', lambda code=1: (_ for _ in ()).throw(ExitCalled()))
    # Patch os.kill to simulate that the fake PID is alive
    monkeypatch.setattr(os, 'kill', lambda pid, sig: None)
    # First instance should succeed
    orch1 = Orchestrator(pid_file=pid_path)
    assert os.path.exists(pid_path)
    # Simulate second instance (should exit)
    # Write a fake PID to the file to simulate another running process
    with open(pid_path, "w") as f:
        f.write("999999")
    with caplog.at_level("INFO"):
        try:
            Orchestrator(pid_file=pid_path)
        except ExitCalled:
            pass
        assert any("already running" in r.message for r in caplog.records)
    # Cleanup
    orch1._release_lock()
    assert not os.path.exists(pid_path)
    # After cleanup, new instance should succeed
    orch2 = Orchestrator(pid_file=pid_path)
    assert os.path.exists(pid_path)
    orch2._release_lock() 