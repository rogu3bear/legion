# Legion: Modular Agent Orchestration System

## Overview
Legion is a sophisticated agent orchestration system built on a canonical layered architecture with robust memory management and strict agent contracts. The system manages agent lifecycles, facilitates message routing, and maintains system state.

## Core Features
- **Modular Agent System**: BaseAgent framework with strict contracts, vector memory, and self-assessment
- **Advanced Memory Management**: Dual vector/SQL storage for semantic search and structured data
- **Task Management**: Priority-based scheduling with real-time status updates
- **Web Interface**: FastAPI backend with WebSockets for real-time updates
- **Discord Integration**: Bot integration with channel-based agent interactions
- **Comprehensive Logging & Telemetry**: Structured JSON logging and metric collection

## Project Status
Current development focus is on completing the web interface backend according to the phases outlined in `BACKEND_IMPLEMENTATION_TRACKER.md`:
- ✅ Phase 0-5 Complete: Setup, Authentication, Core APIs, Task Management, Agent Management, UI Integration
- ⏳ Phase 6 In Progress: Finalizing API Documentation, User Guide, and System Hardening

## Quick Start

### Development
```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make dev
```

### Production
```bash
docker-compose up -d --build
```

## Port Map

| Service | Port |
|---------|------|
| Backend API | 7801 |
| Frontend UI | 7802 |
| Metrics | 7803 |
| Prometheus | 7804 |
| Grafana | 7805 |
| Redis | 7806 |
| Postgres | 7807 |
| Chroma | 7808 |
| Unused | 7809 |
| Reserved | 7810 |

## Tag Glossary

| Tag | Meaning |
|-----|---------|
| 🔑 Core | Required core functionality |
| 💬 Ephemeral | Temporary or short-lived |

## Documentation
For comprehensive documentation, see:
- [Architecture Guide](docs/architecture.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Web Interface Guide](docs/web_interface_guide.md)
- [Discord Integration](docs/discord_integration.md)
- [Function Index](docs/function_index.md)
- [Changelog](changelog.md)

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

## License
All rights reserved. This codebase is proprietary and confidential.
