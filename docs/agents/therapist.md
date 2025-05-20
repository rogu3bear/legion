# Therapist Agent

## Purpose & Responsibilities
Validates intent and sanitizes prompts to enforce policy.

## Handshake Payload
```json
{
  "agent": "therapist",
  "action": "validate_intent"
}
```

## Queue Interaction
Uses `therapist.queue`. Failed tasks are retried twice with increasing delay.

## Failure Modes
On repeated validation failures, tasks are dropped and logged.

## Configuration Keys
- `LLM_MODEL`
- `MAX_RETRIES`
