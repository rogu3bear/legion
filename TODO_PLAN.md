# TODO Review and Action Plan

This document lists all TODO comments discovered in the codebase and proposes next steps.

| File | Line | TODO Summary | Planned Action |
| --- | --- | --- | --- |
| interface/api/v1/endpoints/auth.py | 124 | Implement /refresh endpoint if using refresh tokens. | Add refresh token route via OAuth2; update tests |
| interface/api/v1/endpoints/auth.py | 181 | Implement /refresh endpoint if using refresh tokens. | Add refresh token route via OAuth2; update tests |
| interface/api/v1/endpoints/system.py | 102 | Pass filter parameters in payload if implemented. | Support filtering options and forward to orchestrator |
| interface/api/v1/endpoints/system.py | 92 | Add query parameters for filtering (e.g., level, agent, limit). | Add query params to API schema and service |
| interface/dependencies.py | 94 | More granular role hierarchy could be implemented here. | Introduce role hierarchy enum and update require_role |
| interface/websocket_manager.py | 14 | Add support for rooms/topics if needed later. | Extend manager to group connections by room |
| legion/agents/go/developer.go | 174 | Implement code review logic. | Implement code review handlers |
| legion/agents/go/developer.go | 181 | Implement refactoring logic. | Add refactoring functions |
| legion/agents/go/developer.go | 188 | Implement debugging logic. | Add debugging helpers |
| legion/agents/go/developer.go | 193 | Implement developer agent logic. | Complete agent workflows |
| legion/agents/python/metrics.py | 36 | Implement metrics collection logic. | Gather usage stats from memory |
| legion/agents/python/metrics.py | 41 | Implement metrics analysis logic. | Compute trends and anomalies |
| legion/agents/python/metrics.py | 46 | Implement reporting logic. | Report metrics via Discord or logs |
| legion/core/db_utils.py | 15 | Execute schema.sql or define tables here. | Load schema.sql and create tables |
| legion/core/db_utils.py | 29 | Implement basic migration logic. | Add alembic migration runner |
| legion/orchestrator.py | 1876 | Implement actual task creation logic here. | Create tasks in DB and schedule workers |
| legion/orchestrator.py | 1890 | Fetch task details from StateManager or task queue. | Use StateManager to retrieve task info |
| legion/orchestrator.py | 1901 | Fetch task list from StateManager with filters. | List tasks via StateManager filters |
| legion/orchestrator.py | 1913 | Send cancellation request (e.g., update status, signal worker). | Send cancel signals and update state |
| legion/orchestrator.py | 1925 | Implement actual agent start logic (e.g., process creation, state update). | Spawn process and register state |
| legion/orchestrator.py | 1933 | Implement actual agent stop logic (e.g., signal process, state update). | Signal process stop and update state |
| legion/orchestrator.py | 1941 | Implement actual agent restart logic (stop then start). | Restart process with stop/start sequence |
| legion/orchestrator.py | 2028 | This is a synchronous call to an agent that might be async. | Consider async agent interface |
| legion/orchestrator.py | 2080 | implement routing. | Implement message router |
| legion/orchestrator.py | 2084 | integrate with dispatch pipeline. | Hook to dispatch pipeline function |
| legion/orchestrator.py | 2088 | unify dispatch rules. | Consolidate dispatch rule logic |
| legion/orchestrator.py | 2092 | directive registry hookup. | Connect to directive registry |
| middleware/docs/architecture.md | 49 | TODO section listing middleware tasks. | Follow architecture TODO list: auth, orchestrator wiring, logging, Prometheus, Helm charts |
| middleware/src/main.py | 42 | attach core directives, forward to orchestrator, handle response. | Implement forwarding logic and response handling |
| middleware/src/main.py | 67 | extract agent info, attach context, log to central state. | Add context enrichment and centralized logging |
| middleware/src/middleware/context_manager.py | 11 | enrich context with system directives and metadata. | Attach directives and metadata to requests |
| middleware/src/middleware/context_manager.py | 15 | write to central state repo or database. | Persist interaction logs to state store |
| middleware/src/models.py | 20 | define request schema. | Create Pydantic model for request |
| middleware/src/models.py | 25 | define response schema. | Create Pydantic response model |
| tests/discord/test_health_cog.py | 147 | Mock the interaction with the orchestrator when implemented. | Use fixtures to simulate orchestrator replies |
| tests/test_websockets.py | 90 | Add test for the actual background task if feasible (might require more complex mocking). | Investigate async background task mocking |
| mypy.ini | 5 | sqlalchemy plugin missing | Install SQLAlchemy or adjust mypy config |
