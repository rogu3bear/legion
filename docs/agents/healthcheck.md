# Healthcheck Agent

## Purpose & Responsibilities
Monitors CPU, RAM, and container health.

## Handshake Payload
```json
{
  "agent": "healthcheck",
  "action": "collect_health"
}
```

## Queue Interaction
Reports via `health.queue`. Retries once on network failure.

## Failure Modes
Prolonged failures trigger alerts via the orchestrator.

## Configuration Keys
- `ALERT_CHANNEL`
