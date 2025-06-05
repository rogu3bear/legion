"""API endpoints for task management via the Orchestrator."""

import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import Response

from interface import dependencies
from interface.crud.crud_task import cancel_task, create_task, get_task, list_tasks
from interface.models.user import User
from interface.schemas.task import Task, TaskCreate, TaskCreatedResponse

# Router for task management
router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/"
    response_model=TaskCreatedResponse
    status_code=status.HTTP_201_CREATED
    summary="Submit New Task"
)
def post_task(
    task_in: TaskCreate,
    current_user: User = Depends(dependencies.get_current_active_user),
) -> TaskCreatedResponse:
    """
    Submits a new task to the Legion Orchestrator for processing.

    - **task_in**: Details of the task to be created (title, description, assigned agent).

    Returns the newly created task details, including its assigned ID.
    Requires an active user session.
    Raises HTTP 502 if communication with the orchestrator fails.
    """
    result = create_task(task_in)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY
            detail="Failed to create task in orchestrator"
        )
    return result


@router.get("/", response_model=List[Task], summary="List Tasks")
def read_tasks(
    skip: int = Query(0, description="Number of tasks to skip.", ge=0),
    limit: int = Query(
        100, description="Maximum number of tasks to return.", ge=1, le=200,
    )
    agent: Optional[str] = Query(
        None, description="Filter tasks by assigned agent name.",
    )
    task_status: Optional[str] = Query(
        None, description="Filter tasks by status (e.g., pending, completed, failed).",
    )
    current_user: User = Depends(dependencies.get_current_active_user),
) -> List[Task]:
    """
    Retrieves a list of tasks from the Orchestrator, with optional filtering and pagination.

    - **skip**: Number of initial tasks to skip (for pagination).
    - **limit**: Maximum number of tasks per page.
    - **agent**: Filter by agent name.
    - **task_status**: Filter by task status.

    Requires an active user session.
    Raises HTTP 502 if communication with the orchestrator fails.
    """
    # Note: CRUD function expects agent_id, but API uses agent name for usability
    # The CRUD layer or Orchestrator should handle this mapping if needed
    result = list_tasks(skip=skip, limit=limit, agent_id=agent, status=task_status)
    if result is None or result.tasks is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY
            detail="Failed to retrieve tasks from orchestrator"
        )
    return result.tasks


@router.get("/{task_id}", response_model=Task, summary="Get Task Details")
def read_task(
    task_id: uuid.UUID = Path(..., description="The UUID of the task to retrieve."),
    current_user: User = Depends(dependencies.get_current_active_user),
) -> Task:
    """
    Retrieves the details and current status of a specific task by its UUID.

    - **task_id**: The UUID of the task.

    Requires an active user session.
    Raises HTTP 404 if the task is not found.
    """
    task = get_task(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            detail="Task not found"
        )
    return task


@router.delete(
    "/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Cancel Task"
)
def delete_task(
    task_id: uuid.UUID = Path(..., description="The UUID of the task to cancel."),
    current_user: User = Depends(dependencies.get_current_active_user),
) -> Response:
    """
    Requests the cancellation of an existing task by its UUID.

    - **task_id**: The UUID of the task to cancel.

    Note: Cancellation might not be immediate depending on the task state and Orchestrator logic.
    Requires an active user session.
    Returns HTTP 204 No Content on successful cancellation request.
    Raises HTTP 502 if the cancellation request fails in the orchestrator.
    """
    success = cancel_task(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY
            detail="Failed to cancel task in orchestrator"
        )
    # No content to return on successful deletion
    return Response(status_code=status.HTTP_204_NO_CONTENT)
