import uuid

from legion.orchestrator import state_repo


def test_register_and_fetch_agent():
    agent_id = str(uuid.uuid4())
    token = state_repo.register_agent(agent_id, "worker", ["do"])
    assert token
    record = state_repo.get_agent(agent_id)
    assert record is not None
    assert record.token == token
    assert record.role == "worker"


def test_get_agent_tasks_empty():
    agent_id = str(uuid.uuid4())
    state_repo.register_agent(agent_id, "role", [])
    tasks = state_repo.get_agent_tasks(agent_id)
    assert tasks == []
