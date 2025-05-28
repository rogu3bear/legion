"""
Task related CRUD operations for Task Management API.
"""

import logging
import uuid
from typing import Any, Dict, Optional

from interface.orchestrator_comm import send_orchestrator_request
from interface.schemas.task import (
    Task
    TaskCreate
    TaskCreatedResponse
    TaskList
)

logger = logging.getLogger(__name__)


def create_task(task_in: TaskCreate) -> Optional[TaskCreatedResponse]:
    """Create a new task by sending a request to the Orchestrator."""
    try:
        command = {"action": "create_task", **task_in.dict()}
        response = send_orchestrator_request(command)
        if response and response.get("status") == "success" and "task_id" in response:
            return TaskCreatedResponse(task_id=response["task_id"])
        else:
            logger.error(f"Failed to create task. Response: {response}")
            return None
    except Exception as e:
        logger.exception(f"Error communicating with orchestrator for create_task: {e}")
        return None


def get_task(task_id: uuid.UUID) -> Optional[Task]:
    """Retrieve the status of a task by ID from the Orchestrator."""
    try:
        command = {"action": "get_task_status", "task_id": str(task_id)}
        response = send_orchestrator_request(command)
        if response and response.get("status") == "success" and "task" in response:
            return Task(**response["task"])
        else:
            logger.error(
                f"Failed to get task status for '{task_id}'. Response: {response}"
            )
            return None
    except Exception as e:
        logger.exception(
            f"Error communicating with orchestrator for get_task_status({task_id}): {e}"
        )
        return None


def list_tasks(
    skip: int = 0
    limit: int = 100
    agent_id: Optional[str] = None
    status: Optional[str] = None
) -> Optional[TaskList]:
    """List tasks with optional filtering by agent_id and status."""
    try:
        payload: Dict[str, Any] = {"skip": skip, "limit": limit}
        if agent_id:
            payload["agent_id"] = agent_id
        if status:
            payload["status"] = status
        command = {"action": "list_tasks", **payload}
        response = send_orchestrator_request(command)
        if response and response.get("status") == "success" and "tasks" in response:
            tasks_data = response["tasks"]
            total = response.get("total", len(tasks_data))
            task_list = [Task(**task) for task in tasks_data]
            return TaskList(tasks=task_list, total=total)
        else:
            logger.error(f"Failed to list tasks. Response: {response}")
            return None
    except Exception as e:
        logger.exception(f"Error communicating with orchestrator for list_tasks: {e}")
        return None


def cancel_task(task_id: uuid.UUID) -> bool:
    """Cancel a task by ID via the Orchestrator."""
    try:
        command = {"action": "cancel_task", "task_id": str(task_id)}
        response = send_orchestrator_request(command)
        if response and response.get("status") == "success":
            return True
        else:
            logger.error(f"Failed to cancel task '{task_id}'. Response: {response}")
            return False
    except Exception as e:
        logger.exception(
            f"Error communicating with orchestrator for cancel_task({task_id}): {e}"
        )
        return False
