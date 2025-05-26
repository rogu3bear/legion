# NOTE: The previous version of this file (HEAD) implemented a ZMQ publisher for workload events.
# The current version (main) uses a FIFO queue with priority, backed by StateRepo.
# If ZMQ event publishing is needed, consider integrating the HEAD logic as a utility.

"""Simple PUB socket for workload events.

Events are broadcast on ``tcp://127.0.0.1:${LEGION_PORT_MAP['zmq_pub']}``.
Example payload::

    {"event": "task_assigned", "agent_id": "echo", "task_id": "123"}
"""

from __future__ import annotations

import zmq

from legion.ports import LEGION_PORT_MAP


class WorkloadQueue:
    """Publish agent and task events via ZMQ."""

    def __init__(self) -> None:
        self.context = zmq.Context.instance()
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(f"tcp://127.0.0.1:{LEGION_PORT_MAP['zmq_pub']}")

    def publish(self, event: str, agent_id: str, task_id: str | None = None) -> None:
        payload = {"event": event, "agent_id": agent_id}
        if task_id is not None:
            payload["task_id"] = task_id
        self.publisher.send_json(payload)
