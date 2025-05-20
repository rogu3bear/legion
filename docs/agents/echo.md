# Echo Agent

## Purpose & Responsibilities
The Echo agent mirrors any message it receives.  It is mainly used for
diagnostics and to collect conversation transcripts for later review.

## Handshake
Agents register with the orchestrator by calling
`POST /agent/register` with their ``id``, ``role`` and capability list.
The Echo agent advertises the capability ``echo_task``.
Upon successful registration a token is returned which must be included in
subsequent requests.
```json
{
  "agent": "echo",
  "action": "echo_task"
}
```

## Queue Interaction
Receives tasks on `echo.queue`.  Messages are also broadcast over ZMQ on port
7809 and logged to the Redis list ``echo:log``.

## Failure Modes
High volume may flood logs or Redis memory.  If the agent crashes during
processing the orchestrator will simply drop the message.

## Configuration Keys
- `OUTPUT_CHANNEL`
