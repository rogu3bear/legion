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
   # Start Discord bot
   ./scripts/start_bot.sh
   
   # Start web interface
   ./scripts/start_web.sh
   ```

4. Docker Deployment (Alternative)
   ```bash
   docker-compose up -d
   ```

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

## License
All rights reserved. This codebase is proprietary and confidential. 