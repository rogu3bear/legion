# Workload Queue Protocol

This queue publishes agent registration and task assignment events over ZMQ.
Messages are sent on `tcp://127.0.0.1:7808` (see `LEGION_PORT_MAP['zmq_pub']`).

Example payload:

```json
{"event": "task_assigned", "agent_id": "echo", "task_id": "123"}
```

The `event` field may be `agent_registered` or `task_assigned`.
