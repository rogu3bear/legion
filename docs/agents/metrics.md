# Metrics Agent

## Purpose & Responsibilities
Collects runtime metrics and exposes them to Prometheus.

## Handshake Payload
```json
{
  "agent": "metrics",
  "action": "record_counter"
}
```

## Queue Interaction
Metrics are pushed to `metrics.queue`. Ack on success; no retries.

## Failure Modes
If metric push fails, the event is logged but not retried.

## Configuration Keys
- `EXPORT_PORT`
- `PUSH_GATEWAY`
