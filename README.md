# Legion: Modular Agent Orchestration System

## Overview
Legion is a sophisticated agent orchestration system built on a canonical layered architecture with robust memory management and MCP (Model Context Protocol) integration. The system manages agent lifecycles, facilitates message routing, and maintains system state with modern development tool integration.

## Core Features
- **Modular Agent System**: BaseAgent framework with strict contracts and vector memory
- **Advanced Memory Management**: Dual vector/SQL storage for semantic search and structured data
- **Task Management**: Priority-based scheduling with real-time status updates
- **Agent Registration**: Agents obtain persistent tokens via `/agent/register`
- **Web Interface**: FastAPI backend with authentication and real-time updates
- **Discord Integration**: Bot integration with channel-based agent interactions
- **MCP Integration**: Model Context Protocol servers for AI development tools (Cursor IDE)
- **Comprehensive Logging & Telemetry**: Structured JSON logging and metric collection

## Project Status
<!-- reviewme: BACKEND_IMPLEMENTATION_TRACKER.md referenced but doesn't exist - need to verify current phase status -->
Current development focus is on MCP integration and web interface stabilization. The system includes:
- ✅ Core Infrastructure: Authentication, APIs, Task Management, Agent Management
- ✅ MCP Servers: Unified MCP system for Cursor IDE integration
- ⏳ In Progress: Documentation updates and system optimization

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

### 🩺 Quick Start Check

```bash
git clone <repository-url>
cd legion
make doctor   # env sanity
make dev      # launch full stack, Ctrl-C to stop
```

#### Local Redis Setup
```bash
# macOS
brew install redis
redis-server --port 7600  &

# Ubuntu / Debian
sudo apt-get install redis-server
redis-server --port 7600  &
```

*Note: Keep `LEGION_REDIS_PORT=7600` in your `.env.ports` file.*

## MCP Integration
Legion provides unified **MCP (Model Context Protocol)** servers that integrate with modern AI development tools like Cursor IDE. The MCP system exposes Legion's capabilities as tools that AI assistants can use during development workflows.

### Quick MCP Setup for Cursor IDE
```bash
# Automated setup - configures Cursor with Legion MCP tools
./scripts/setup_cursor_mcp.sh

# Test the integration
python scripts/test_mcp_setup.py
```

**Available MCP Tools:**
- Vector memory operations for contextual information storage
- Smart caching with TTL expiration
- Event logging and querying by severity/type
- Codebase analysis with change detection
- DevOps operations monitoring

**Quick Start:** [2-Minute MCP Setup Guide](docs/mcp_quickstart.md)
**Detailed Guide:** [MCP Cursor Integration](docs/mcp_cursor_integration.md)

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
| Orchestrator | PORT_ALLOCATOR_ORCHESTRATOR | 7601 |
| Web UI | PORT_ALLOCATOR_WEB_UI | 7602 |
| Redis | LEGION_REDIS_PORT | 7600 |
| Postgres | PORT_ALLOCATOR_POSTGRES | 7650 |

### Agent Prompt Editor
Prompts can be edited live at:
http://localhost:7602/admin/agent-prompts

✔️ Edits apply immediately to running agents (if they are active and listening).
↩️ Use the Revert button in the edit modal to restore the last saved version of a prompt.

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

### Dev Guide

```bash
make doctor   # Validate env
make dev      # Launch orchestrator + UI
```

* UI: [http://localhost:7602](http://localhost:7602)
* Agent Admin: `/admin/agent-prompts`

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

<!-- reviewme: Scaffolding Roadmap section may be outdated - verify these files still exist and are relevant -->
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
