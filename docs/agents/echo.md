# Echo Agent

## Purpose & Responsibilities
Echoes commands for audit and training data.

## Handshake Payload
```json
{
  "agent": "echo",
  "action": "echo_task"
}
```

## Queue Interaction
Receives tasks on `echo.queue`. Immediate ack; failures do not retry.

## Failure Modes
High volume may flood logs; monitor channel routing.

## Configuration Keys
- `OUTPUT_CHANNEL`
