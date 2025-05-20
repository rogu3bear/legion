# Service Ports

| Port | Service | Rationale |
| ---- | ------- | --------- |
| 7801 | Web UI backend | FastAPI app |
| 7802 | Web UI frontend | Vite dev server |
| 7803 | REST API | Orchestrator routes |
| 7804 | Interface API | Internal use |
| 7805 | Middleware | Request filters |
| 7806 | Metrics | Prometheus exporter |
| 7807 | Researcher API | Data fetcher |
| 7808 | Orchestrator PUB | Message bus |
| 7809 | Orchestrator SUB | Message bus |
| 7810 | Redis | Queue storage |
