import os
import pytest
import json
from legion.agents.python.metrics import MetricsAgent
from legion.agents.python.therapist import TherapistAgent

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
    agent = MetricsAgent("metrics", None, 1)
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
    agent = TherapistAgent("therapist", None, 1)
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
    agent = MetricsAgent("metrics", None, 1)
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
    agent = TherapistAgent("therapist", None, 1)
    agent.set_log_paths(log_path=test_env["log_path"])
    summary = agent.compose_summary()
    assert "Session started" in summary 