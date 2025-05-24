# Legion Architecture
High-level overview of orchestrator, agents, Redis queue, and ZMQ bus.
→ Full diagrams: [../legacy/Legion Architecture and Diagrams.md]
=======

Legion is organized as a strict multi-layer system that separates external interfaces from core orchestration. Agents communicate over a ZeroMQ message bus while the orchestrator coordinates state updates and task routing. Redis queues provide transient storage and the memory subsystem persists long term data to both vector stores and relational databases. A FastAPI service exposes REST and WebSocket endpoints, allowing real-time interactions via a web UI and Discord bot. Middleware filters requests and enforces policy before they reach the orchestrator. This layered approach ensures that each component remains decoupled yet observable, enabling independent scaling and clear fault boundaries. Logging and metrics are pushed to a Prometheus exporter so operators can monitor health across containers. Overall the architecture favors small, specialized agents connected by a robust messaging fabric while maintaining a single source of truth for system state.

👉 For details see [legacy/Legion Architecture and Diagrams.md]
