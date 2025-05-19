# Monorepo Architecture Blueprint

```mermaid
flowchart TD
    subgraph Backend
        A[FastAPI] --> B[Orchestrator]
        B --> C[(Redis)]
        B --> D[(PostgreSQL)]
    end
    subgraph Frontend
        E[Vite + React]
    end
    subgraph Agents
        F[Worker Pool]
    end
    A <--> E
    B <--> F
    B --> LM[LM Studio API]
```

### Directory Layout
```
/backend     # FastAPI app and business logic
/frontend    # React UI powered by Vite
/scripts     # Utility scripts
/docs        # Documentation
/tests       # Pytest and Jest suites
```
\nThe orchestrator communicates with worker agents through a registration handshake and a priority-based task queue in Redis.
