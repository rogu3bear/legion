import logging
import os
import sys
import tempfile
import pytest

from legion.orchestrator import Orchestrator


def test_agent_channel_ids_not_empty():
    from legion.orchestrator import Orchestrator

    orchestrator = Orchestrator()
    assert (
        orchestrator.agent_channel_ids
    ), "agent_channel_ids should not be empty after startup"


def test_duplicate_startup_and_cleanup(monkeypatch, caplog):
    # Use a temp PID file location
    tmp_pid = tempfile.NamedTemporaryFile(delete=False)
    tmp_pid.close()
    pid_path = tmp_pid.name

    # Patch sys.exit to raise a custom exception
    class ExitCalled(Exception):
        pass

    monkeypatch.setattr(sys, "exit", lambda code=1: (_ for _ in ()).throw(ExitCalled()))
    # Patch os.kill to simulate that the fake PID is alive
    monkeypatch.setattr(os, "kill", lambda pid, sig: None)
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


def test_unknown_config_key_logs_warning(tmp_path, caplog, monkeypatch):
    # write a temp YAML with a valid agent plus 'foo: bar'
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("therapist_agent:\n  model: gpt-4\nfoo: bar\n")
    monkeypatch.setenv("ORCH_CONFIG_PATH", str(cfg))
    from legion.orchestrator import Orchestrator

    caplog.set_level(logging.WARNING)
    Orchestrator()
    assert "Ignoring unknown config key: foo" in caplog.text


def test_orchestrator_custom_dependencies():
    class DummyStateManager:
        def __init__(self):
            self.touched = False
        def log_task(self, task):
            self.touched = True
    class DummyLLMClient:
        def __init__(self):
            self.touched = False
            self.model = "dummy"
            self.default_kwargs = {}
        def generate(self, *a, **k):
            self.touched = True
            return "ok"
    dummy_state = DummyStateManager()
    dummy_llm = DummyLLMClient()
    orch = Orchestrator(state_manager=dummy_state, llm_client=dummy_llm)
    # Should use dummy_state for logging
    orch.state.log_task({"foo": "bar"})
    assert dummy_state.touched
    # Should use dummy_llm for agent LLMs
    for agent in orch.agents.values():
        assert agent.llm is dummy_llm
        agent.llm.generate("agent", "thread", {}, [{"role": "user", "content": "hi"}])
        assert dummy_llm.touched


@pytest.mark.asyncio
async def test_orchestrator_agent_interaction():
    """Test interaction between orchestrator and multiple agents."""
    orchestrator = Orchestrator()
    orchestrator.register_test_agents()
    
    # Simulate message dispatch to multiple agents
    response1 = await orchestrator.dispatch_message("TestAgent1", "Hello Agent 1")
    response2 = await orchestrator.dispatch_message("TestAgent2", "Hello Agent 2")
    
    assert response1 is not None, "Orchestrator should return response from Agent 1"
    assert response2 is not None, "Orchestrator should return response from Agent 2"
    assert "Agent 1" in response1, "Response should mention Agent 1"
    assert "Agent 2" in response2, "Response should mention Agent 2"


@pytest.mark.asyncio
async def test_orchestrator_error_handling():
    """Test orchestrator's error handling for invalid agent or message."""
    orchestrator = Orchestrator()
    orchestrator.register_test_agents()
    
    try:
        response = await orchestrator.dispatch_message("InvalidAgent", "Test message")
        assert response is not None, "Orchestrator should handle invalid agent gracefully"
    except Exception as e:
        pytest.fail(f"Orchestrator failed to handle error: {str(e)}")
