"""Redis-backed priority queue interface.

enqueue(task: dict, priority: int = 5) -> str
    Enqueue a task and return its id.

dequeue() -> dict | None
    Retrieve the highest priority task or ``None`` if empty.

retry(task_id: str) -> None
    Requeue the task with incremented retry count.
"""

# TODO: full impl; provide docstring spec + logging.


