import json
import logging
import time

import pytest

from legion.agents.base import BaseAgent
from legion.agents.python.architect import ArchitectAgent
from legion.agents.python.doctor import DoctorAgent
from legion.agents.python.echo import EchoAgent
from legion.agents.python.healthcheck import HealthcheckAgent
from legion.agents.python.metrics import MetricsAgent
from legion.agents.python.ping import PingAgent
from legion.agents.python.researcher import ResearcherAgent
from legion.agents.python.therapist import TherapistAgent
from legion.agents.python.ux_designer import UxDesignerAgent


@pytest.fixture(scope="module")
def test_env(tmp_path_factory):
    logs_dir = tmp_path_factory.mktemp("logs")
    reports_dir = tmp_path_factory.mktemp("reports")
    db_dir = tmp_path_factory.mktemp("db")
    log_path = logs_dir / "task_log.jsonl"
    report_path = reports_dir / "llm_connector_test.log"
    db_path = db_dir / "legion.db"
    open(log_path, "w").close()
    open(report_path, "w").close()
    open(db_path, "w").close()
    yield {
        "log_path": str(log_path),
        "report_path": str(report_path),
        "db_path": str(db_path),
        "logs_dir": str(logs_dir),
        "reports_dir": str(reports_dir),
        "db_dir": str(db_dir),
    }


@pytest.mark.asyncio
async def test_metrics_agent_reads_task_log(test_env, monkeypatch):
    entries = [
        {"type": "metric", "content": "CPU usage"},
        {"type": "metric", "content": "Memory usage"},
    ]
    with open(test_env["log_path"], "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
    agent = MetricsAgent(DummyOrchestrator())
    agent.name = "metrics"
    agent.client = DummyClient()
    agent.channel_id = 1
    agent.config = {}
    agent.set_log_paths(log_path=test_env["log_path"])
    logs = agent.read_logs()
    assert logs == entries


@pytest.mark.asyncio
async def test_therapist_agent_reads_task_log(test_env, monkeypatch):
    entries = [
        {"type": "therapy", "content": "Session started"},
        {"type": "therapy", "content": "Session ended"},
    ]
    with open(test_env["log_path"], "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
    agent = TherapistAgent(DummyOrchestrator())
    agent.name = "therapist"
    agent.client = DummyClient()
    agent.channel_id = 1
    agent.config = {}
    agent.set_log_paths(log_path=test_env["log_path"])
    logs = agent.read_logs()
    assert logs == entries


@pytest.mark.asyncio
async def test_metrics_agent_composes_summary(test_env, monkeypatch):
    entries = [
        {"type": "metric", "content": "CPU usage"},
    ]
    with open(test_env["log_path"], "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
    agent = MetricsAgent(DummyOrchestrator())
    agent.name = "metrics"
    agent.client = DummyClient()
    agent.channel_id = 1
    agent.config = {}
    agent.set_log_paths(log_path=test_env["log_path"])
    summary = agent.compose_summary()
    assert "CPU usage" in summary


@pytest.mark.asyncio
async def test_therapist_agent_composes_summary(test_env, monkeypatch):
    entries = [
        {"type": "therapy", "content": "Session started"},
    ]
    with open(test_env["log_path"], "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
    agent = TherapistAgent(DummyOrchestrator())
    agent.name = "therapist"
    agent.client = DummyClient()
    agent.channel_id = 1
    agent.config = {}
    agent.set_log_paths(log_path=test_env["log_path"])
    summary = agent.compose_summary()
    assert "Session started" in summary


class DummyOrchestrator:
    agent_channel_ids = {
        "architect_agent": 1,
        "doctor_agent": 2,
        "echo_agent": 3,
        "healthcheck_agent": 4,
        "ping_agent": 5,
        "researcher_agent": 6,
        "therapist_agent": 7,
        "ux_designer_agent": 8,
    }


class DummyClient:
    def get_channel(self, channel_id):
        return None


def test_agent_instantiation_and_properties():
    agent_classes = [
        ArchitectAgent,
        DoctorAgent,
        EchoAgent,
        HealthcheckAgent,
        PingAgent,
        ResearcherAgent,
        TherapistAgent,
        UxDesignerAgent,
    ]
    names = [
        "architect_agent",
        "doctor_agent",
        "echo_agent",
        "healthcheck_agent",
        "ping_agent",
        "researcher_agent",
        "therapist_agent",
        "ux_designer_agent",
    ]
    for cls, name in zip(agent_classes, names):
        agent = cls(DummyOrchestrator())
        agent.name = name
        agent.client = DummyClient()
        agent.channel_id = DummyOrchestrator().agent_channel_ids[name]
        agent.config = {"default_prompt": "stub"}
        assert agent.name == name
        assert agent.client is not None
        assert agent.channel_id == DummyOrchestrator().agent_channel_ids[name]
        assert agent.config["default_prompt"] == "stub"


class DummyBaseAgent(BaseAgent):
    async def self_assess(self):
        self._assess_count = getattr(self, "_assess_count", 0) + 1
        return "ok"


def test_self_assessment_scheduler_guard(monkeypatch):
    agent = DummyBaseAgent(orchestrator=None)
    agent._assess_count = 0
    # Patch logging to capture INFO logs
    logs = []
    monkeypatch.setattr(logging, "info", lambda msg, *a, **k: logs.append(msg))
    # Start first loop
    started1 = agent.start_self_assessment(interval_seconds=1)
    # Start second loop (should not start)
    started2 = agent.start_self_assessment(interval_seconds=1)
    time.sleep(2)
    agent.stop_self_assessment()
    # Only one loop should be running
    assert started1 is True
    assert started2 is False
    # Should log about duplicate start
    assert any("already running" in m for m in logs)
    # Should have run self_assess at least once
    assert agent._assess_count >= 1
