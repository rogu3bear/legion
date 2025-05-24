# Operations & Deployment
Docker-Compose stack, health-checks, port map (7801-7810).
See ../legacy/ops/ for full run-book.

=======

Legion services run in Docker containers orchestrated with `docker-compose`. The stack includes the orchestrator, individual agents, a Redis instance, and a Prometheus exporter. Environment variables in `.env` and `.env.ports` define network bindings and credentials. During development `make dev` spins up the full suite, while CI uses the same compose files for integration tests. Production deployments mount persistent volumes for memory stores and run behind a reverse proxy. Containers expose minimal ports and rely on health checks to restart if an agent becomes unresponsive. Logs are forwarded to the host for centralized analysis.
👉 More: legacy/ops/*

=======
# Operations Notes

- Base image now python:3.10-slim to ensure build compatibility.
