# Legion: Comprehensive Reference Guide

## Table of Contents
1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Web Interface](#web-interface)
5. [Agent System](#agent-system)
6. [Memory System](#memory-system)
7. [Discord Integration](#discord-integration)
8. [Security](#security)
9. [Deployment](#deployment)
10. [Development Standards](#development-standards)
11. [Testing Strategy](#testing-strategy)
12. [Troubleshooting](#troubleshooting)
13. [API Reference](#api-reference)
14. [WebSocket Reference](#websocket-reference)
15. [ZeroMQ IPC Reference](#zeromq-ipc-reference)

## Introduction

Legion is a modular agent orchestration system built on a canonical layered architecture with sophisticated memory management and strict agent contracts. This reference guide provides comprehensive documentation on utilizing the Legion system, with a focus on standards, patterns, and security use cases.

### Key Features
- **Modular Agent System**: Independent agents with strict interfaces
- **Dual Memory System**: Vector embeddings and SQL-based storage
- **Structured Logging**: JSON logs for enhanced telemetry
- **Web Interface**: FastAPI backend with WebSocket support
- **Discord Integration**: Bot-based interaction
- **ZeroMQ IPC**: Efficient inter-process communication

### Core Principles
1. **Modularity**: Each agent is an independent unit with a strict interface
2. **Extensibility**: New agents can be added without modifying the orchestrator
3. **Resilience**: Failures in one agent don't cascade to others
4. **Observability**: Structured logging and metrics collection

## System Architecture

Legion follows a strict 8-layer architecture, enforced by CI:

1. **Configuration Layer**: YAML agent definitions, `.env` variables
2. **Orchestration Layer**: Central "brain" for agent management
3. **Agent Layer**: Persona runtime code
4. **Skill & Utility Layer**: Reusable helpers
5. **Persistence Layer**: SQLite DB, memory API, JSONL logs
6. **Integration Layer**: Discord-bot glue
7. **Presentation Layer**: Web UI (FastAPI endpoints)
8. **Infrastructure Layer**: Ops-focused tooling

### Data Flow
1. **Incoming Message**: Discord → Bot → Orchestrator Cog → Orchestrator
2. **Routing**: Orchestrator → Target Agent (based on channel or content)
3. **Processing**: Agent → Memory/Skills → Response
4. **Response**: Agent → Orchestrator → Discord
5. **Logging**: All steps logged in structured JSON format

## Core Components

### Orchestrator
- **Role**: Central router and scheduler
- **Key Methods**:
  - `load_configs()`: Reads YAML files for agent definitions
  - `dispatch_message()`: Routes incoming messages to appropriate agents
  - `post_to_discord()`: Sends responses back to Discord channels
  - `reload_configs()`: Dynamically updates agent configurations

### Dependency Injection
- **Container**: `legion/core/di_container.py` manages service dependencies
- **Interfaces**: `legion/core/interfaces.py` defines service contracts
- **Services**:
  - `ILLMClient`: Contract for LLM interactions
  - `IStateManager`: Contract for state management
  - `IMemoryManager`: Contract for memory system

### Logging & Telemetry
- **Structured Logging**: JSON format via `legion/core/logging_config.py`
- **Log Location**: `scripts/logs/`
- **Format**: Defined in `legion/core/logging_config.py`
- **Access**: Use `make logs` to view recent logs

## Web Interface

The Legion web interface provides a comprehensive control plane for the system, built with FastAPI and WebSockets.

### Backend Components
1. **FastAPI Application**: Core web server
2. **Database Layer**: SQLAlchemy ORM with SQLite
3. **Authentication & Authorization**: JWT-based with RBAC
4. **Orchestrator Integration**: ZeroMQ REQ/REP IPC
5. **WebSocket Manager**: Real-time updates

### API Endpoints

#### Authentication (`/api/v1/auth`)
- `POST /login`: User login, returns JWT tokens
- `POST /logout`: User logout (server-side token invalidation)
- `POST /refresh`: Obtain new access token using refresh token
- `GET /me`: Get current authenticated user's details

#### Agents (`/api/v1/agents`)
- `GET /`: List all registered agents with status
- `GET /{agent_name}`: Get detailed status for a specific agent
- `POST /{agent_name}/dispatch`: Send a message/command to the agent
- `GET /{agent_name}/history`: Get paginated conversation history
- `GET /{agent_name}/config`: Get current configuration
- `PUT /{agent_name}/config`: Update agent configuration
- `POST /{agent_name}/assess`: Trigger agent self-assessment
- `POST /{agent_name}/start|stop|restart`: Control agent lifecycle

#### System (`/api/v1/system`)
- `GET /status`: Get overall system status
- `GET /metrics`: Get detailed system metrics
- `GET /logs`: Get paginated and filterable system logs
- `GET /memory/stats`: Get memory system usage statistics
- `GET /config`: Get current system-level configuration
- `PUT /config`: Update system-level configuration

#### Memory (`/api/v1/memory`)
- `GET /agents/{agent_name}/search`: Search a specific agent's vector memory
- `GET /search`: Search across all agent memories
- `GET /documents`: List available documents
- `GET /documents/{doc_name}`: Retrieve a specific document

#### Tasks (`/api/v1/tasks`)
- `POST /`: Submit a new task
- `GET /`: List tasks with filters
- `GET /{task_id}`: Get details of a specific task
- `DELETE /{task_id}`: Cancel a task

### WebSocket Endpoints
- `/ws/events`: Streams real-time system events
- `/ws/agents/{agent_name}/feed`: Real-time updates for a specific agent
- `/ws/system/metrics`: Streams key system metrics

### Database Schema

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

#### User Preferences Table
```sql
CREATE TABLE user_preferences (
    user_id INTEGER PRIMARY KEY,
    theme TEXT DEFAULT 'dark',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### Audit Log Table
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    target_resource TEXT,
    details TEXT,
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Agent System

### BaseAgent
- **Core Class**: All agents inherit from `BaseAgent`
- **Interface**: Defined in `legion/agents/contracts.py`
- **Key Methods**:
  - `handle_message()`: Process incoming messages
  - `validate_request()`: Validate message content
  - `fallback_response()`: Generate fallback responses
  - `self_assess()`: Evaluate agent performance

### Agent Types
- **Architect**: Plans multi-step tasks and coordinates other agents
- **Doctor/Researcher**: Specialized for analysis and data synthesis
- **Metrics Agent**: Collects and analyzes system performance data

### Agent Development
1. **Contract Compliance**: Implement interfaces from `legion/agents/contracts.py`
2. **Base Functionality**: Extend `BaseAgent` for core capabilities
3. **Memory Integration**: Use provided memory management methods
4. **Error Handling**: Follow established error boundary patterns
5. **Testing**: Implement required test coverage

## Memory System

### Dual Storage
- **Vector Storage**: Embeddings for semantic search
- **SQL Storage**: Structured data (task metadata, agent state)
- **API**: `LegionMemory` class provides unified access
- **Logs**: JSONL files for task history and debugging

### Memory Operations
- **Retrieval**: `retrieve_memories()` for semantic search
- **Storage**: `store_memories()` for saving new information
- **Deduplication**: Prevents duplicate memory storage
- **Versioning**: Supports document versioning

## Discord Integration

### Bot Core
- **File**: `integration/discord/bot.py`
- **Cogs**:
  - **Orchestrator Cog**: Bridges Discord events to the orchestrator
  - **Health Cog**: Provides status and diagnostics commands
  - **UX Feed Cog**: Manages user experience feedback loops

### Event Handlers
- `on_ready()`: Initializes bot and logs connection
- `on_message()`: Processes incoming messages and routes to orchestrator

### Commands
- `ping()`: Simple health check
- `health()`: Detailed system status
- `config_agent()`: Updates agent configurations via Discord

## Security

### Authentication & Authorization
- **JWT Tokens**: Short-lived access tokens with refresh tokens
- **Password Hashing**: bcrypt for secure password storage
- **RBAC**: Role-based access control (Admin, AgentOperator, User)
- **Token Validation**: Middleware for JWT validation

### Data Protection
- **HTTPS**: Enforced via reverse proxy or ASGI server
- **Input Validation**: Pydantic for rigorous schema validation
- **Output Encoding**: Sanitization of user-provided input
- **Security Headers**: CSP, HSTS, X-Frame-Options, etc.

### API Security
- **Rate Limiting**: Applied to sensitive endpoints
- **CORS**: Configured to allow only trusted origins
- **CSRF Protection**: For cookie-based sessions

### Session Management
- **Secure Token Handling**: HttpOnly cookies for refresh tokens
- **Token Revocation**: Mechanisms for logout and security events

### Dependency Management
- **Vulnerability Scanning**: Dependabot, `safety`
- **Secrets Management**: Environment variables, secrets manager

### Logging & Auditing
- **Audit Logs**: Detailed logs for security-sensitive actions
- **Sensitive Data**: Avoid logging passwords, tokens, etc.

## Deployment

### Environment Setup
1. **Create `.env`**: Copy `.env.example` to `.env`
2. **Populate Secrets**: Fill in required values
3. **Dependencies**: Use a Python virtual environment

### Memory System Setup
```bash
# Grant execution permissions
chmod +x scripts/*.sh

# Initialize memory system
./scripts/init_memory.sh
```

### Agent Deployment
1. **Configuration**: Place agent YAML configs in `config/agents/`
2. **Dependencies**: Ensure all required packages are installed
3. **Startup**: Use the provided scripts

### Web Interface Deployment
1. **Dependencies**: Install web interface requirements
2. **Environment**: Configure web-specific environment variables
3. **Startup**: Use the provided script
4. **Access**: API at `http://localhost:8000/api/v1`, WebSocket at `ws://localhost:8000/ws`
5. **Authentication**: Create an admin user

### CI/CD Pipeline
1. **Lint**: Runs flake8 and mypy
2. **Test**: Executes pytest suite
3. **Build**: Creates deployment artifacts
4. **Deploy**: Deploys to production (if on main branch)

## Development Standards

### Code Style
- **Modules**: snake_case
- **Classes**: PascalCase
- **Functions**: snake_case
- **Type Annotations**: Mandatory for all function signatures
- **Docstrings**: Clear documentation for all public modules, classes, and functions

### Project Structure
- **Core**: `legion/core/` for core utilities
- **Agents**: `legion/agents/` for agent implementations
- **Memory**: `legion/memory/` for memory system
- **Integration**: `integration/` for external integrations
- **Interface**: `backend/` (currently `interface/`) for web interface
- **Skills**: `skills/` for reusable skills
- **Tests**: `tests/` for test suites

### Dependency Management
- **Python**: `requirements.txt` for Python dependencies
- **Go**: `go.mod` and `go.sum` for Go dependencies
- **JavaScript**: `package.json` for frontend dependencies

### Version Control
- **Branching**: GitHub Flow for development
- **Commits**: Small, atomic commits with clear messages
- **Pull Requests**: Against the `main` branch with reviews

## Testing Strategy

### Unit Tests
- **Location**: `tests/agents/`, `tests/core/`
- **Focus**: Agent logic, skills, utilities
- **Tools**: pytest, unittest.mock

### Integration Tests
- **Location**: `tests/test_orchestrator.py`
- **Focus**: Message routing, Discord events
- **Tools**: pytest, pytest-asyncio

### Contract Tests
- **Location**: `tests/agents/test_agent_contracts.py`
- **Focus**: Validate agent interfaces
- **Tools**: pytest

### Performance Tests
- **Location**: `tests/test_orchestrator.py`
- **Focus**: Measure latency for message dispatch
- **Tools**: pytest, time measurement

### Security Tests
- **Location**: `tests/api/v1/test_auth.py`
- **Focus**: Scan for API key leaks or unsafe calls
- **Tools**: bandit, safety

## Troubleshooting

### Memory System
- **Issue**: "Database not initialized"
  - **Solution**: Run `./scripts/init_memory.sh`

### Agent Issues
- **Issue**: "Agent failed to start"
  - **Solution**: Check agent YAML config and logs

### Web Interface
- **Issue**: "Cannot connect to WebSocket"
  - **Solution**: Ensure orchestrator is running and ZeroMQ ports are accessible
- **Issue**: "Authentication failed"
  - **Solution**: Check JWT token expiration and secret key configuration
- **Issue**: "CORS errors"
  - **Solution**: Verify WEB_CORS_ORIGINS in .env includes your frontend origin

### General
- **Issue**: "Missing environment variables"
  - **Solution**: Copy `.env.example` to `.env` and fill in values
- **Issue**: "Permission denied"
  - **Solution**: Run `chmod +x scripts/*.sh`

## API Reference

### Authentication API

#### Login
- **Endpoint**: `POST /api/v1/auth/login`
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "string",
    "token_type": "bearer",
    "refresh_token": "string"
  }
  ```

#### Get Current User
- **Endpoint**: `GET /api/v1/auth/me`
- **Headers**: `Authorization: Bearer {token}`
- **Response**:
  ```json
  {
    "id": 1,
    "username": "string",
    "email": "string",
    "role": "string",
    "is_active": true,
    "created_at": "string",
    "last_login": "string"
  }
  ```

### Agents API

#### List Agents
- **Endpoint**: `GET /api/v1/agents`
- **Headers**: `Authorization: Bearer {token}`
- **Response**:
  ```json
  {
    "agents": [
      {
        "name": "string",
        "status": "string",
        "uptime": "string",
        "messages_processed": 0
      }
    ]
  }
  ```

#### Get Agent Status
- **Endpoint**: `GET /api/v1/agents/{agent_name}`
- **Headers**: `Authorization: Bearer {token}`
- **Response**:
  ```json
  {
    "name": "string",
    "status": "string",
    "uptime": "string",
    "messages_processed": 0,
    "last_message": "string",
    "last_message_time": "string",
    "error_count": 0,
    "last_error": "string",
    "last_error_time": "string"
  }
  ```

#### Dispatch Message to Agent
- **Endpoint**: `POST /api/v1/agents/{agent_name}/dispatch`
- **Headers**: `Authorization: Bearer {token}`
- **Request Body**:
  ```json
  {
    "message": "string",
    "thread_id": "string"
  }
  ```
- **Response**:
  ```json
  {
    "status": "string",
    "message_id": "string",
    "timestamp": "string"
  }
  ```

### System API

#### Get System Status
- **Endpoint**: `GET /api/v1/system/status`
- **Headers**: `Authorization: Bearer {token}`
- **Response**:
  ```json
  {
    "orchestrator_status": "string",
    "uptime": "string",
    "agent_count": 0,
    "active_agents": 0,
    "error_count": 0,
    "last_error": "string",
    "last_error_time": "string"
  }
  ```

#### Get System Metrics
- **Endpoint**: `GET /api/v1/system/metrics`
- **Headers**: `Authorization: Bearer {token}`
- **Response**:
  ```json
  {
    "cpu_usage": 0.0,
    "memory_usage": 0.0,
    "disk_usage": 0.0,
    "network_io": {
      "bytes_sent": 0,
      "bytes_received": 0
    },
    "agent_metrics": [
      {
        "name": "string",
        "llm_latency": 0.0,
        "processing_time": 0.0,
        "token_usage": 0
      }
    ]
  }
  ```

### Memory API

#### Search Memory
- **Endpoint**: `GET /api/v1/memory/search`
- **Headers**: `Authorization: Bearer {token}`
- **Query Parameters**:
  - `query`: Search query text
  - `agent_name`: Optional agent name to filter by
  - `limit`: Maximum number of results (default: 10)
- **Response**:
  ```json
  {
    "results": [
      {
        "text": "string",
        "agent_name": "string",
        "timestamp": "string",
        "score": 0.0
      }
    ]
  }
  ```

#### List Documents
- **Endpoint**: `GET /api/v1/memory/documents`
- **Headers**: `Authorization: Bearer {token}`
- **Query Parameters**:
  - `agent_name`: Optional agent name to filter by
  - `limit`: Maximum number of results (default: 20)
  - `offset`: Pagination offset (default: 0)
- **Response**:
  ```json
  {
    "documents": [
      {
        "id": "string",
        "name": "string",
        "agent_name": "string",
        "created_at": "string",
        "updated_at": "string",
        "version": 0
      }
    ],
    "total": 0
  }
  ```

### Tasks API

#### Create Task
- **Endpoint**: `POST /api/v1/tasks`
- **Headers**: `Authorization: Bearer {token}`
- **Request Body**:
  ```json
  {
    "agent_name": "string",
    "task_type": "string",
    "parameters": {
      "key": "value"
    },
    "priority": 0
  }
  ```
- **Response**:
  ```json
  {
    "task_id": "string",
    "status": "string",
    "created_at": "string"
  }
  ```

#### List Tasks
- **Endpoint**: `GET /api/v1/tasks`
- **Headers**: `Authorization: Bearer {token}`
- **Query Parameters**:
  - `agent_name`: Optional agent name to filter by
  - `status`: Optional status to filter by
  - `limit`: Maximum number of results (default: 20)
  - `offset`: Pagination offset (default: 0)
- **Response**:
  ```json
  {
    "tasks": [
      {
        "task_id": "string",
        "agent_name": "string",
        "task_type": "string",
        "status": "string",
        "created_at": "string",
        "updated_at": "string",
        "completed_at": "string",
        "result": "string"
      }
    ],
    "total": 0
  }
  ```

## WebSocket Reference

### Events WebSocket

#### Connection
- **Endpoint**: `ws://localhost:8000/ws/events`
- **Authentication**: JWT token in query parameter (`?token=...`)

#### Message Format
```json
{
  "type": "string",
  "timestamp": "string",
  "data": {
    // Event-specific data
  }
}
```

#### Event Types
- `agent_status_update`: Agent status changes
- `system_metric_update`: System metric updates
- `task_update`: Task status updates
- `error`: System errors

### Agent Feed WebSocket

#### Connection
- **Endpoint**: `ws://localhost:8000/ws/agents/{agent_name}/feed`
- **Authentication**: JWT token in query parameter (`?token=...`)

#### Message Format
```json
{
  "type": "string",
  "timestamp": "string",
  "data": {
    // Agent-specific data
  }
}
```

#### Event Types
- `thought_process`: Agent's internal thought process
- `memory_access`: Memory retrieval or storage
- `llm_request`: LLM API request details
- `llm_response`: LLM API response details
- `error`: Agent-specific errors

## ZeroMQ IPC Reference

### REQ/REP Pattern

#### Request Format
```json
{
  "action": "string",
  "request_id": "string",
  // Action-specific parameters
}
```

#### Response Format
```json
{
  "status": "string",
  "request_id": "string",
  // Action-specific response data
}
```

### Common Actions

#### Status
- **Request**:
  ```json
  {
    "action": "status",
    "request_id": "uuid"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "request_id": "uuid",
    "orchestrator_status": "string",
    "uptime": "string",
    "agent_count": 0,
    "active_agents": 0
  }
  ```

#### List Agents
- **Request**:
  ```json
  {
    "action": "list_agents",
    "request_id": "uuid"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "request_id": "uuid",
    "agents": [
      {
        "name": "string",
        "status": "string",
        "uptime": "string",
        "messages_processed": 0
      }
    ]
  }
  ```

#### Create Task
- **Request**:
  ```json
  {
    "action": "create_task",
    "request_id": "uuid",
    "agent_name": "string",
    "task_type": "string",
    "parameters": {
      "key": "value"
    },
    "priority": 0
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "request_id": "uuid",
    "task_id": "string"
  }
  ```

#### Get Task Status
- **Request**:
  ```json
  {
    "action": "get_task_status",
    "request_id": "uuid",
    "task_id": "string"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "request_id": "uuid",
    "task": {
      "task_id": "string",
      "agent_name": "string",
      "task_type": "string",
      "status": "string",
      "created_at": "string",
      "updated_at": "string",
      "completed_at": "string",
      "result": "string"
    }
  }
  ```

#### Cancel Task
- **Request**:
  ```json
  {
    "action": "cancel_task",
    "request_id": "uuid",
    "task_id": "string"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "request_id": "uuid"
  }
  ```

### Error Handling

#### Error Response Format
```json
{
  "status": "error",
  "request_id": "string",
  "error": {
    "code": "string",
    "message": "string",
    "details": "string"
  }
}
```

#### Common Error Codes
- `invalid_action`: Unknown action requested
- `invalid_parameters`: Missing or invalid parameters
- `not_found`: Requested resource not found
- `permission_denied`: Insufficient permissions
- `internal_error`: Internal server error
