# Ping Agent

## Purpose & Responsibilities
Provides simple liveness checks and measures round-trip latency.

## Handshake Payload
```json
{
  "agent": "ping",
  "action": "ping"
}
```

## Queue Interaction
Uses `ping.queue` for requests. No retries are performed.

## Failure Modes
If a ping fails, the orchestrator reports the agent as offline.

## Configuration Keys
- `SLEEP_SECONDS`
