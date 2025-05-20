# UX Designer Agent

## Purpose & Responsibilities
Improves prompts and UI micro-interactions.

## Handshake Payload
```json
{
  "agent": "ux_designer",
  "action": "rewrite_text"
}
```

## Queue Interaction
Work is queued on `ux.queue`. Tasks retry once if the agent fails.

## Failure Modes
After two failures the orchestrator logs and drops the task.

## Configuration Keys
- `LLM_MODEL`
