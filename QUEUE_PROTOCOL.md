# Workload Queue Protocol

This document describes how agents interact with the Legion Orchestrator's persistent workload queue.

## Lifecycle

```mermaid
sequenceDiagram
    participant Agent
    participant Orchestrator
    participant Queue
    Agent->>Orchestrator: POST /agent/register
    Orchestrator->>Queue: dequeue(agent)
    Orchestrator-->>Agent: task_assigned (ZMQ PUB)
    Agent->>Orchestrator: ZMQ SUB subscribe for tasks
    Agent->>Orchestrator: task complete
```

1. **Registration** – Agents send `POST /agent/register` with their `id`, `role`, and `capabilities`. The orchestrator stores metadata and publishes `agent_registered`.
2. **Enqueue** – Tasks are added via internal calls to `WorkloadQueue.enqueue`. Items persist in `memory/state/repo.json`.
3. **Delegation** – When an agent registers or the queue receives a new task, the orchestrator matches by capability and assigns the next task, publishing `task_assigned`.
4. **Completion** – Agents report completion via existing channels (not covered here).

Use `/queue/summary` and `/agent/{id}/tasks` to inspect queue state.
