"""Directive routing helpers for the Orchestrator."""
from __future__ import annotations

import uuid
from typing import Any

from legion.task_queue import Task, queue

# Track threads we have seen to send intro messages only once per thread
_KNOWN_THREADS: set[str] = set()
# TODO: Persist thread history in state_repo to survive restarts


def process_directive(payload: dict[str, Any]) -> str:
    """Process an incoming directive payload.

    If this is the first time we've seen the ``thread_id`` in ``payload``
    then an ``intro`` flag is added so the receiving agent can introduce
    itself. The payload is enqueued as a :class:`~legion.task_queue.Task`.

    Parameters
    ----------
    payload:
        Dictionary containing at least ``agent`` and ``directive`` keys.

    Returns
    -------
    str
        The ID of the created task.
    """
    agent = payload.get("agent")
    directive = payload.get("directive")
    if not agent or not directive:
        raise ValueError("payload must include 'agent' and 'directive'")

    thread_id = payload.get("thread_id")
    if thread_id and thread_id not in _KNOWN_THREADS:
        payload["intro"] = True
        _KNOWN_THREADS.add(thread_id)
    else:
        payload.setdefault("intro", False)

    task = Task(id=str(uuid.uuid4()), agent=agent, payload=payload)
    queue.enqueue(task)
    return task.id
