# Legion: Modular Agent Orchestration System

## Overview
Legion is a sophisticated agent orchestration system built on a canonical layered architecture with robust memory management and strict agent contracts. The system manages agent lifecycles, facilitates message routing, and maintains system state.

## Core Features
- **Modular Agent System**: BaseAgent framework with strict contracts, vector memory, and self-assessment
- **Advanced Memory Management**: Dual vector/SQL storage for semantic search and structured data
- **Task Management**: Priority-based scheduling with real-time status updates
- **Agent Registration**: Agents obtain persistent tokens via `/agent/register`
- **Web Interface**: FastAPI backend with WebSockets for real-time updates
- **Discord Integration**: Bot integration with channel-based agent interactions
- **Comprehensive Logging & Telemetry**: Structured JSON logging and metric collection

## Project Status
Current development focus is on completing the web interface backend according to the phases outlined in `BACKEND_IMPLEMENTATION_TRACKER.md`:
- ✅ Phase 0-5 Complete: Setup, Authentication, Core APIs, Task Management, Agent Management, UI Integration
- ⏳ Phase 6 In Progress: Finalizing API Documentation, User Guide, and System Hardening

## Quick Start
1. Environment Setup
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Initialize System
   ```bash
   ./scripts/init_memory.sh
   ```

3. Start Services
   ```bash
   make dev
   ```

4. Lint and Test
   ```bash
   make lint
 make test
  ```
5. Run integration smoke test
   ```bash
   python scripts/integration_smoke.py
   ```
6. Docker Deployment (Alternative)
   ```bash
   docker-compose up -d
   ```

## Tooling: Offline Install
To install dev tools (pipdeptree, safety, pytest) offline, run:
```bash
./scripts/setup_offline_tools.sh
```
- The script is idempotent and uses a local wheel cache if present (./wheels or ./artifacts/wheels).
- Falls back to online install if no wheels are found.

## Testing
Run the built-in handshake test locally with:
```bash
make test
```
This executes `scripts/selftest_handshake.py` and prints `[HANDSHAKE TEST] PASS` on success.

### Development Ports
| Service | Env Var | Default |
|---------|---------|---------|
| Orchestrator | PORT_ALLOCATOR_ORCHESTRATOR | 27000 |
| Web UI | PORT_ALLOCATOR_WEB_UI | 27001 |
| Redis | PORT_ALLOCATOR_REDIS | 27040 |
| Postgres | PORT_ALLOCATOR_POSTGRES | 27050 |


## Documentation
For comprehensive documentation, see:
- [Documentation Index](docs/README.md)
- [Function Index](docs/system/function_index.md)
- [Changelog](changelog.md)

## Full System Operation

Below is a high‑level view of how the pieces fit together when all services are running:

```
   +---------+     +--------------+     +---------------+
   |  User   +---> |  Interfaces  +---> |  Orchestrator |
   +---------+     +--------------+     +---------------+
                                       /               \
                                      v                 v
                               +-----------+    +---------------+
                               |   Agents  |    | Monitoring/DB |
                               +-----------+    +---------------+
```

### Message Handling Pipeline

```
User
  |
  v
[Discord/Web/API] --dispatch_message--> [Orchestrator]
  |
  v
[BaseAgent]
   |-- validate_request
   |-- retrieve_memories
   |-- build_prompt
   |-- call_llm
   |-- store_memories
   '-- post_to_discord
  |
  v
User receives reply
```

## Project Structure
Legion follows a strict layered architecture enforced by CI:
1. **Configuration Layer**: YAML agent definitions, environment variables
2. **Orchestration Layer**: The core system that manages agents and routes messages
3. **Agent Layer**: Persona runtime code for various agent types
4. **Skill & Utility Layer**: Reusable skills and utilities
5. **Persistence Layer**: Memory system with vector and SQL storage
6. **Integration Layer**: Discord-bot integration
7. **Presentation Layer**: Web UI with FastAPI backend
8. **Infrastructure Layer**: CI/CD, scripts, documentation

## Development
1. Follow the canonical structure (enforced by CI)
2. Ensure comprehensive test coverage
3. Update documentation when adding features
4. Maintain the changelog

## MCP Stack
The **MCP** (Modular Control Plane) stack coordinates core services and tool
invocations. This release introduces the foundational scaffolding and database
schema for upcoming functionality.

## Agent Instantiation Guard
**Purpose:** Prevent direct construction of agent classes outside the orchestrator.

**How it works:** A pre-commit hook and a CI job run `scripts/agent_instantiation_guard.py` on the `legion/` directory to detect improper instantiations.

**Local usage:**
```bash
# Check for direct instantiations
python scripts/agent_instantiation_guard.py legion/

# Apply automatic fixes
python scripts/agent_instantiation_guard.py --apply legion/
```

Use the `orchestrator.load_agent()` API to instantiate agents correctly.

## Tag Glossary
`agents` — core personas
`tasks` — orchestrator routes
`registry_tasks` — public task registry endpoints

## Scaffolding Roadmap
The table below tracks scaffolded files introduced by Codex.

| Path | Purpose |
|------|---------|
| `core/` | Wrapper exposing `legion.core` modules |
| `core/utils/network.py` | Re-exports network helpers |
| `core/utils/indexing.py` | Re-exports indexing helpers |
| `core/db/migrations/` | Core database migrations |
| `legion/agents/python/doctor.py` | Doctor agent implementation |
| `legion/agents/python/researcher.py` | Researcher agent implementation |

## License
All rights reserved. This codebase is proprietary and confidential.
