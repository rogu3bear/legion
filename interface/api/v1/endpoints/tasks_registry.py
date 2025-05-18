"""API endpoints for the in-memory task registry."""

from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Path, Query, status

from interface.schemas.task_registry import Task, TaskStatus, TaskUpdate
from legion.orchestrator import state_repo as state_repository

router = APIRouter()


@router.get("/", response_model=List[Task])
def list_tasks(
    status: Optional[TaskStatus] = Query(None),
    owner: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
) -> List[Task]:
    """Return tasks filtered by optional query parameters."""
    tasks = state_repository.list_tasks(status=status, owner=owner, tag=tag)
    return [Task(**task.__dict__) for task in tasks]


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: str = Path(...)) -> Task:
    """Retrieve a single task by ID."""
    task = state_repository.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return Task(**task.__dict__)


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: Task) -> Task:
    """Add a task to the registry."""
    task_id = task.id or str(uuid4())
    state_repository.add_task(task_id, tags=task.tags, owner=task.owner or "")
    stored = state_repository.get_task(task_id)
    assert stored
    return Task(**stored.__dict__)


@router.patch("/{task_id}", response_model=Task)
def update_task(task_id: str = Path(...), payload: TaskUpdate | None = None) -> Task:
    """Update fields of an existing task."""
    task = state_repository.update_task(
        task_id, status=payload.status if payload else None, tags=payload.tags if payload else None, owner=payload.owner if payload else None
    )
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return Task(**task.__dict__)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str = Path(...)) -> None:
    """Remove a task from the registry."""
    if not state_repository.remove_task(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return None
