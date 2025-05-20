# Architect Agent

## Purpose & Responsibilities
Designs high-level blueprints and multi-step plans.

## Handshake Payload
```json
{
  "agent": "architect",
  "action": "create_plan"
}
```

## Queue Interaction
Tasks are enqueued to `architect.tasks`. The agent acknowledges on completion and retries once on failure.

## Failure Modes
If planning fails, the orchestrator retries with backoff. After two failures the task is marked errored.

## Configuration Keys
- `LLM_MODEL`
- `PLAN_TIMEOUT`
