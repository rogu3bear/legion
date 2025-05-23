# Function Flow Diagrams (ASCII)

This document illustrates how user requests move through the Legion system.

## User Entry Points
```
User
  |-- Discord Bot
  |-- Web UI / REST API
  |-- WebSocket Feed
```
All entry points funnel into the **Interface** layer which forwards requests to the orchestration pipeline.

## Orchestrator Pipeline
```
[Interface]
     |
[Middleware]
     |
[Orchestrator]
     |
[TherapistAgent]
     |
[Specific Agent]
     |
[Memory & LLM]
     |
[Specific Agent]
     |
[Orchestrator]
     |
[Interface]
     v
   User
```

## Agent Execution Steps
```
+------------------+
|    BaseAgent     |
+------------------+
| validate_payload |
| retrieve_memories|
| perform_task     |
| store_memories   |
| build_response   |
+------------------+
```

These ASCII diagrams summarise the end-to-end flow, from user interaction to the underlying agent functions.
