<!-- File: docs/architecture/ports.md -->

# Legion Port Map

The following ports are reserved for Legion services. Values are fixed and
should remain within **27000-28000**. See `legion/ports.py` for the source of

truth.
| Service | Port |
|--------------------|------|
| Orchestrator REST | 27000 |
| UI Web | 27001 |
| Chroma | 27020 |
| Prometheus | 27030 |
| Redis | 27040 |
| Postgres | 27050 |
| Grafana | 27060 |
| ZMQ PUB | 27070 |
| ZMQ REP | 27071 |
| Therapist Agent | 27080 |
| Executor Agent | 27081 |
| Architect Agent | 27082 |
| Metrics Agent | 27083 |
