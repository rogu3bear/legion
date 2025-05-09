# FAQ

## Architectural Guidelines

### Why can't I instantiate agents directly?

All agents must be created via `orchestrator.load_agent()` to ensure proper lifecycle management, configuration loading, caching, and initialization. Direct instantiation (e.g., `ArchitectAgent(...)`) bypasses these orchestrator checks and will be flagged by the Agent Instantiation Guard scripts (pre-commit hook and CI job).

Use:
```python
agent = orchestrator.load_agent('<agent_key>')
``` 