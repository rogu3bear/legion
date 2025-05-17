import uuid

from legion.core.constants import TaskState
from legion.orchestrator.state_repository import add_task, get_task, update_task_status


def test_add_and_retrieve_task():
    task_id = str(uuid.uuid4())
    add_task(task_id, tags=["demo"], owner="tester", agent="architect")
    task = get_task(task_id)
    assert task is not None
    assert task.owner == "tester"
    assert task.status == TaskState.PENDING


def test_update_task_status():
    task_id = str(uuid.uuid4())
    add_task(task_id, tags=[], owner="tester")
    assert update_task_status(task_id, TaskState.ACTIVE)
    task = get_task(task_id)
    assert task.status == TaskState.ACTIVE

