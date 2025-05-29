<!-- File: research/metrics_tech_brief.md -->

# Metrics Agent & Observability Design Brief

## Overview
This brief outlines a lightweight metrics collection strategy for Legion. The system must run offline but scale when Redis and Prometheus are available.

## Core KPIs
- **Queue Depth** – size of the primary task queue and dead-letter queue.
- **Agent Uptime** – heartbeat timestamp compared to threshold.
- **Error Rate** – counts of failed tasks and exceptions.
- **Task Latency** – time between dispatch and completion.

## Sampling Cadence
- Default cadence: **1 Hz** (once per second) per metric.
- **Push vs Pull**:
  - *Push:* agents write metrics to Redis hashes every cycle.
  - *Pull:* a Prometheus exporter reads from Redis or in-memory data when available.

## Redis Data Model
- Use hash key `metrics:latest` for current values.
- Incrementing counters stored under `metrics:<name>:total`.
- Optionally keep a capped list `metrics:<name>:ts` for time series (timestamp, value).

## Prometheus Exposition Snippet
```text
# TYPE legion_queue_depth gauge
legion_queue_depth{queue="task"} 5
legion_queue_depth{queue="dead_letter"} 0
# TYPE legion_agent_uptime counter
legion_agent_uptime{agent="orchestrator"} 1020
```

## Discord Embed Example
```json
{
  "content": null,
  "embeds": [
    {
      "title": "Metrics Update",
      "description": "Queue: 5 tasks\nErrors: 0\nLatency avg: 120 ms",
      "color": 5814783
    }
  ]
}
```

## Reference Patterns
1. **Prometheus Client Python (BSD-2-Clause)**
   - Minimal API to define counters and histograms.
   - Start HTTP server in a single call.
   - Well documented; heavy when collecting many metrics.
2. **StatsD Client (MIT)**
   - UDP-based; non-blocking and lightweight.
   - Requires external aggregator such as Telegraf or Datadog.
   - Simple counters/timers, but lacks labels by default.
3. **OpenTelemetry Collector (Apache-2.0)**
   - Pluggable pipeline; supports OTLP, Prometheus, and others.
   - Larger footprint but standardizes metrics and tracing.
   - Can run as sidecar for richer telemetry.

## Security & Performance Notes
- Provide an offline stub when Redis or Prometheus are not available. The stub simply logs metrics to local files.
- Rate limit updates to Discord to avoid spamming: e.g., send summaries every minute.
- Truncate logs older than a week to prevent unbounded disk growth.
- Store tokens and secrets only in environment variables; never commit them to git.

## Implementation Checklist
- [ ] Implement Redis hash storage as described.
- [ ] Create a Prometheus exporter reading from Redis if available.
- [ ] Add Discord bridge to post daily summaries to `#agent-feed`.
- [ ] Include offline stub fallback when dependencies are missing.
- [ ] Write unit tests for exporter and Redis interactions under `tests/`.
- [ ] Run `make lint` and `make test` before committing changes.

## Appendix
**Glossary**
- **KPI:** Key Performance Indicator.
- **Exporter:** Service exposing metrics to Prometheus.
- **Redis Hash:** Key-value map stored at a single Redis key.
- **OTLP:** OpenTelemetry Protocol.

**References**
- Prometheus Python Client – https://github.com/prometheus/client_python
- StatsD – https://github.com/statsd/statsd
- OpenTelemetry Collector – https://github.com/open-telemetry/opentelemetry-collector

## Detailed Design
A single MetricsAgent instance runs in a background loop. When Redis is detected it pushes metrics to the `metrics:latest` hash. Each metric is stored with a numeric value and the agent also increments the matching `metrics:<name>:total` counter. When Redis is unavailable the agent writes to a local file under `memory/logs/metrics.jsonl` so the data persists between runs. The exporter process periodically reads the latest metrics and exposes them to Prometheus on port 7606.

The queue depth metrics are gathered via the Legion task queue interface. The agent counts the sorted set length when using Redis and falls back to the in-memory store otherwise. Agent uptime is tracked by recording a `start_time` and computing the difference with `time.monotonic()` each cycle. Error rate is derived from logs: failed tasks increment a `error_count` field that resets daily. Task latency requires storing dispatch timestamps; the agent subtracts start and completion times to produce a histogram bucket in Prometheus.

## Scaling Strategy
While offline, metrics are captured locally and posted to Discord at a low frequency. As soon as Redis becomes available the agent begins pushing to the central store. The Prometheus exporter can then be enabled to scrape the data. This dual-mode approach avoids any hard dependency on external services but allows scaling to multiple nodes when they exist. Redis key expiry should be configured on the time-series lists to prevent unlimited growth. Sharded Redis setups are supported because each key is independent.

## Discord Reporting
Metrics summaries should be concise. The example embed above can be generated using the Discord API. Color coding can indicate severity (green for normal, yellow for warnings). Longer reports should be uploaded as files rather than embed descriptions to reduce noise in the channel.

## Operational Concerns
Testing of the MetricsAgent is best done with Redis mocked by the `fakeredis` library. Unit tests should verify that hashes are updated and counters incremented correctly. Integration tests can spin up a real Redis instance via Docker. The agent must handle Redis connection errors gracefully and continue operating in offline mode without crashing.

Ensure that the Prometheus endpoint does not expose sensitive data. Only aggregate metrics should be published. When running in production behind a gateway, restrict access to `/metrics` to internal services.


## Future Enhancements
- **Tracing Integration:** adopt OpenTelemetry spans to correlate metrics with request traces.
- **Anomaly Detection:** run a simple moving average to flag spikes in latency or error rate.
- **Agent Self-Assessment:** feed metrics back into the Planner agent to schedule maintenance tasks.
- **Web Dashboard:** surface metrics and alerts in the Legion UI for quick diagnostics.

A small proof-of-concept of these ideas can be built with current stdlib packages and expanded later when internet access is available. The MetricsAgent should be designed with extension hooks so new collectors or exporters can register themselves without changing core logic. Extensive documentation should accompany each new component so that future maintainers can operate the system in restricted environments.

## Conclusion
Implementing a dedicated MetricsAgent with offline-safe defaults will provide clear visibility into Legion's behavior even in constrained environments. The combination of Redis for ephemeral storage, Prometheus for long-term monitoring, and Discord for human-readable summaries creates a layered observability stack that scales with available infrastructure. Careful attention to security and resource usage ensures the system remains lightweight while still delivering actionable data.
