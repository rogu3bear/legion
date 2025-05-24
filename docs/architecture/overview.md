# Architecture Overview

Legion follows a layered model separating interfaces, orchestrator logic, agents, and memory stores. A ZeroMQ bus handles internal messaging while Redis queues transient tasks. Persistent data lives in vector and relational stores. A FastAPI service provides REST and WebSocket APIs for the Discord bot and web UI.

See the diagrams in this folder for sequence flows and container layouts.
