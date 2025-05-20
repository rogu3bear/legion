import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

import pytest
from interface.core.config import settings
from interface.schemas.task import Task, TaskCreatedResponse, TaskList

# Assuming fixtures `client` and `normal_user_token_headers` are available


@patch("interface.crud.crud_task.create_task")
def test_post_task_success(
    mock_create, client: TestClient, normal_user_token_headers: dict
):
    """Test successful task submission."""
    task_id = uuid.uuid4()
    mock_create.return_value = TaskCreatedResponse(task_id=task_id)
    payload = {
        "agent_id": "agent123",
        "type": "typeA",
        "priority": 2,
        "title": "Test Task",
        "description": "Task description",
        "metadata": {"key": "value"},
    }
    response = client.post(
        f"{settings.API_V1_STR}/tasks",
        json=payload,
        headers=normal_user_token_headers,
    )
    assert response.status_code == 201
    assert response.json() == {
        "message": "Task submitted successfully.",
        "task_id": str(task_id),
    }
    mock_create.assert_called_once()


@patch("interface.crud.crud_task.create_task")
def test_post_task_failure(
    mock_create, client: TestClient, normal_user_token_headers: dict
):
    """Test task submission failure."""
    mock_create.return_value = None
    payload = {"agent_id": "a", "type": "t", "title": "t"}
    response = client.post(
        f"{settings.API_V1_STR}/tasks",
        json=payload,
        headers=normal_user_token_headers,
    )
    assert response.status_code == 502
    assert "Failed to create task" in response.json()["detail"]


@pytest.mark.asyncio
async def test_post_task_unauthorized(client: TestClient):
    """Test submitting task without auth."""
    response = client.post(f"{settings.API_V1_STR}/tasks", json={})
    assert response.status_code == 401


@patch("interface.crud.crud_task.list_tasks")
def test_get_tasks_success(
    mock_list, client: TestClient, normal_user_token_headers: dict
):
    """Test listing tasks successfully."""
    sample_tasks = [
        {
            "id": str(uuid.uuid4()),
            "agent_id": "agent1",
            "status": "pending",
            "priority": 1,
            "title": "t1",
            "description": None,
            "metadata": None,
            "result": None,
            "created_at": "2024-01-01T00:00:00Z",
            "started_at": None,
            "completed_at": None,
            "error": None,
        },
    ]
    task_objs = [Task(**task) for task in sample_tasks]
    mock_list.return_value = TaskList(tasks=task_objs, total=1)
    response = client.get(
        f"{settings.API_V1_STR}/tasks?skip=0&limit=10",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert isinstance(body["tasks"], list)
    mock_list.assert_called_once_with(skip=0, limit=10, agent_id=None, status=None)


@patch("interface.crud.crud_task.list_tasks")
def test_get_tasks_failure(
    mock_list, client: TestClient, normal_user_token_headers: dict
):
    """Test listing tasks failure."""
    mock_list.return_value = None
    response = client.get(
        f"{settings.API_V1_STR}/tasks",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 502
    assert "Failed to retrieve tasks" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_tasks_unauthorized(client: TestClient):
    """Test listing tasks without auth."""
    response = client.get(f"{settings.API_V1_STR}/tasks")
    assert response.status_code == 401


@patch("interface.crud.crud_task.get_task")
def test_read_task_success(
    mock_get, client: TestClient, normal_user_token_headers: dict
):
    """Test retrieving a task successfully."""
    task_id = uuid.uuid4()
    sample = {
        "id": str(task_id),
        "agent_id": "agent1",
        "status": "pending",
        "priority": 1,
        "title": "t1",
        "description": None,
        "metadata": None,
        "result": None,
        "created_at": "2024-01-01T00:00:00Z",
        "started_at": None,
        "completed_at": None,
        "error": None,
    }
    mock_get.return_value = Task(**sample)
    response = client.get(
        f"{settings.API_V1_STR}/tasks/{task_id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["id"] == str(task_id)
    mock_get.assert_called_once_with(task_id)


@patch("interface.crud.crud_task.get_task")
def test_read_task_not_found(
    mock_get, client: TestClient, normal_user_token_headers: dict
):
    """Test retrieving a non-existent task."""
    task_id = uuid.uuid4()
    mock_get.return_value = None
    response = client.get(
        f"{settings.API_V1_STR}/tasks/{task_id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]


@patch("interface.crud.crud_task.cancel_task")
def test_delete_task_success(
    mock_cancel, client: TestClient, normal_user_token_headers: dict
):
    """Test successful task cancellation."""
    task_id = uuid.uuid4()
    mock_cancel.return_value = True
    response = client.delete(
        f"{settings.API_V1_STR}/tasks/{task_id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 204
    mock_cancel.assert_called_once_with(task_id)


@patch("interface.crud.crud_task.cancel_task")
def test_delete_task_failure(
    mock_cancel, client: TestClient, normal_user_token_headers: dict
):
    """Test task cancellation failure."""
    task_id = uuid.uuid4()
    mock_cancel.return_value = False
    response = client.delete(
        f"{settings.API_V1_STR}/tasks/{task_id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 502
    assert "Failed to cancel task" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_task_unauthorized(client: TestClient):
    """Test cancelling a task without auth."""
    task_id = uuid.uuid4()
    response = client.delete(f"{settings.API_V1_STR}/tasks/{task_id}")
    assert response.status_code == 401
