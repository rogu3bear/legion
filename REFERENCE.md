# Legion System Reference Guide

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Core Components](#core-components)
3. [API Reference](#api-reference)
4. [Agent System](#agent-system)
5. [Memory System](#memory-system)
6. [Discord Integration](#discord-integration)
7. [Security](#security)
8. [Deployment](#deployment)
9. [Testing](#testing)
10. [Development Guidelines](#development-guidelines)

## System Architecture

### Overview
Legion is a distributed agent-based system with a modular architecture consisting of:
- Core orchestrator for agent management
- Memory system for persistent storage
- Web interface for API access
- Discord integration for chat-based interaction
- Agent system for autonomous task execution

### Key Components
- `legion/orchestrator.py`: Central system coordinator
- `legion/core/`: Core system functionality
- `legion/agents/`: Agent implementations
- `legion/memory/`: Memory management
- `interface/`: Web API and interface
- `integration/`: External integrations
- `skills/`: Reusable agent capabilities

## Core Components

### Orchestrator
The orchestrator (`legion/orchestrator.py`) manages:
- Agent lifecycle
- Task distribution
- System state
- Resource allocation
- Inter-agent communication

### Core System
Located in `legion/core/`:
- `state.py`: System state management
- `logging_config.py`: Logging configuration
- `llm_client.py`: LLM integration
- `di_container.py`: Dependency injection
- `interfaces.py`: Core interfaces
- `network.py`: Network communication
- `db.py`: Database management

### Memory System
Located in `legion/memory/`:
- Persistent storage
- Document indexing
- Memory retrieval
- Context management

## API Reference

### Authentication
- JWT-based authentication
- Role-based access control
- Token management

### Endpoints
1. Agents API (`/api/v1/agents/`)
   - List agents
   - Get agent status
   - Configure agents
   - Dispatch messages
   - Trigger assessments

2. System API (`/api/v1/system/`)
   - System status
   - Metrics
   - Logs
   - Memory statistics

3. Memory API (`/api/v1/memory/`)
   - List documents
   - Retrieve documents
   - Search memory
   - Global search

4. Tasks API (`/api/v1/tasks/`)
   - Submit tasks
   - List tasks
   - Get task details
   - Cancel tasks

## Agent System

### Base Agent
Located in `legion/agents/base.py`:
- Core agent functionality
- State management
- Task execution
- Memory integration
- Communication protocols

### Agent Types
1. Python Agents
   - Native Python implementation
   - Direct memory access
   - Full system integration

2. Go Agents
   - External process communication
   - Protocol-based interaction
   - Isolated execution

### Agent Contracts
Defined in `legion/agents/contracts.py`:
- Interface definitions
- Communication protocols
- State requirements
- Capability specifications

## Memory System

### Storage
- SQLite database (`legion/memory/db/legion.db`)
- Document indexing
- Context management
- Retrieval optimization

### Features
- Document storage
- Semantic search
- Context retrieval
- Memory persistence
- Cross-agent memory sharing

## Discord Integration

### Bot Implementation
Located in `integration/discord/bot.py`:
- Command handling
- Event processing
- User interaction
- System integration

### Cogs
1. UX Feed (`ux_feed.py`)
   - User experience monitoring
   - Feedback collection
   - Interaction tracking

2. Orchestrator (`orchestrator.py`)
   - System control
   - Agent management
   - Task execution

3. Health (`health.py`)
   - System monitoring
   - Status reporting
   - Health checks

## Security

### Authentication
- JWT token-based
- Role-based access
- Token expiration
- Secure storage

### Authorization
- Role hierarchy
- Permission management
- Access control
- Resource protection

### Data Protection
- Encrypted storage
- Secure communication
- Data isolation
- Access logging

## Deployment

### Scripts
Located in `scripts/`:
- `deploy.sh`: System deployment
- `start_bot.sh`: Bot startup
- `init_memory.sh`: Memory initialization
- `verify_discord.sh`: Discord verification
- `test.sh`: Testing execution

### Configuration
Located in `legion/configs/`:
- `developer.yaml`: Development settings
- `agents.yaml`: Agent configuration
- `discord_channels.yaml`: Discord settings
- Environment-specific configs

## Testing

### Test Structure
Located in `tests/`:
1. API Tests (`tests/api/`)
   - Endpoint testing
   - Authentication
   - Request/response validation

2. Agent Tests (`tests/agents/`)
   - Agent functionality
   - Memory integration
   - Contract compliance

3. Core Tests (`tests/core/`)
   - System functionality
   - Network communication
   - State management

4. Integration Tests (`tests/integration/`)
   - End-to-end testing
   - System interaction
   - Performance testing

5. Discord Tests (`tests/discord/`)
   - Bot functionality
   - Command handling
   - Integration testing

## Development Guidelines

### Code Style
- Python: PEP 8
- Go: Standard Go format
- Documentation: Google style
- Type hints: Required

### Best Practices
1. Testing
   - Unit tests required
   - Integration tests for features
   - Performance benchmarks
   - Security testing

2. Documentation
   - Code comments
   - API documentation
   - Architecture docs
   - Deployment guides

3. Security
   - Input validation
   - Output sanitization
   - Access control
   - Secure defaults

4. Performance
   - Resource optimization
   - Caching strategies
   - Async operations
   - Load testing

### Workflow
1. Development
   - Feature branches
   - Code review
   - Testing
   - Documentation

2. Deployment
   - Staging environment
   - Production deployment
   - Monitoring
   - Rollback procedures

3. Maintenance
   - Regular updates
   - Security patches
   - Performance optimization
   - Bug fixes
