# Legion Web Interface Backend Planning

## 1. Overview

This document outlines the plan for developing a comprehensive, production-grade web interface backend for the Legion agent system. The interface will serve as a primary control plane, offering enhanced capabilities for agent interaction, system monitoring, configuration, and data access, supplementing the existing Discord integration. Adherence to Legion's core principles of modularity, resilience, and observability is paramount.

## 2. Current System Analysis

The Legion system currently consists of:

1.  **Orchestrator**: Central component (`legion/orchestrator.py`) managing agent lifecycles, message routing, and system state via a PID-locked process.
2.  **Agents**: Modular, specialized components (`legion/agents/`) adhering to strict contracts (`legion/agents/contracts.py`).
3.  **Memory System**: Dual-storage (`memory/legion_memory.py`) using vector embeddings (e.g., ChromaDB, FAISS - *TBD*) and SQLite for structured data (`memory/db/legion.db`), with JSONL task logs (`memory/logs/`).
4.  **Discord Integration**: Primary user interface (`integration/discord/`) via cogs and commands.
5.  **Basic Web Interface**: Existing FastAPI app (`interface/main.py`) with basic WebSocket event feed (`/ws/events`, `/ws/feed`).

**Limitations of Current Web Interface:**
- Read-only event feed.
- No user authentication or authorization.
- Lacks agent interaction or configuration capabilities.
- Minimal error handling and observability.

## 3. Requirements

### 3.1. Functional Requirements (FR)

1.  **FR-AgentMgmt-View**: View all registered agents, their status (Idle, Processing, Error), configuration, and basic metrics (e.g., uptime, messages processed).
2.  **FR-AgentMgmt-Config**: Modify agent parameters (model, temperature, max_tokens, custom prompts) via API, persisting changes to agent YAML files or a dedicated config store (*TBD*).
3.  **FR-AgentMgmt-Lifecycle**: Start/stop/restart specific agents via API calls proxied to the Orchestrator.
4.  **FR-AgentMgmt-Assess**: Trigger agent self-assessments (`self_assess` method) via API.
5.  **FR-Comm-Send**: Send messages/commands to specific agents via API, mimicking Discord interaction flow.
6.  **FR-Comm-History**: View paginated conversation history for agent interactions initiated via the web interface.
7.  **FR-Comm-Memory**: Access and search agent vector memories and view relevant stored documents via API.
8.  **FR-Monitor-Health**: View real-time system health metrics (CPU, memory, disk usage, agent status) via API and WebSocket.
9.  **FR-Monitor-Perf**: Monitor agent performance metrics (LLM latency, processing time, token usage) via API.
10. **FR-Monitor-Logs**: Access and filter structured system logs (Orchestrator, Agents, Web backend) via API.
11. **FR-Config-ViewEdit**: View and edit system-level configurations (e.g., logging levels, memory parameters).
12. **FR-UserMgmt-Auth**: Secure user authentication (e.g., username/password, potentially OAuth providers).
13. **FR-UserMgmt-Roles**: Role-based access control (RBAC) defining permissions for different actions (e.g., Admin, Viewer, AgentOperator).
14. **FR-UserMgmt-Prefs**: Allow users to manage preferences (e.g., theme, notification settings).

### 3.2. Non-Functional Requirements (NFR)

1.  **NFR-Perf-Latency**: API endpoints response time < 150ms (p95), < 300ms (p99) under nominal load (50 concurrent users). WebSocket message latency < 500ms.
2.  **NFR-Perf-Concurrency**: Support at least 100 concurrent authenticated users and 200 active WebSocket connections.
3.  **NFR-Perf-Resource**: Backend service resource utilization (CPU, Memory) should remain within defined limits under load.
4.  **NFR-Security-Auth**: All API endpoints (except login/discovery) MUST require valid authentication tokens (JWT). Implement secure password hashing (bcrypt).
5.  **NFR-Security-HTTPS**: Enforce HTTPS for all communication.
6.  **NFR-Security-Vulnerabilities**: Mitigate OWASP Top 10 vulnerabilities (Injection, Broken Auth, XSS, CSRF, Security Misconfig, etc.). Use input validation (Pydantic), output encoding, security headers (via middleware), and CSRF protection tokens.
7.  **NFR-Security-Secrets**: No hardcoded secrets. Utilize environment variables or a dedicated secrets manager (e.g., HashiCorp Vault, AWS Secrets Manager).
8.  **NFR-Security-Dependencies**: Regularly scan dependencies for vulnerabilities (`safety`, Dependabot).
9.  **NFR-Scalability-Horizontal**: Design for statelessness where possible to allow horizontal scaling of the web backend service (multiple instances behind a load balancer). Database scaling to be addressed separately if needed.
10. **NFR-Scalability-DB**: Ensure efficient database queries through proper indexing and ORM usage. Implement connection pooling.
11. **NFR-Reliability-Errors**: Implement comprehensive error handling with standardized error responses (e.g., JSON structure with error codes and messages). Gracefully handle Orchestrator/Agent unavailability.
12. **NFR-Reliability-Recovery**: Implement basic health checks (`/health`) for load balancers/orchestration. Aim for automatic recovery where feasible.
13. **NFR-Reliability-Logging**: Maintain comprehensive structured JSON logs with correlation IDs for request tracing.
14. **NFR-Maintainability-Code**: Adhere to Legion coding style (`project_config.md`), use type hints (`mypy`), enforce code quality (`ruff`), and aim for high test coverage. Follow principles of robust Python code [Cite: Python Robustness Tips](https://dev.to/uponthesky/pythontips-for-writing-robust-python-code-functions-2g2k).
15. **NFR-Testability**: Design for testability with clear separation of concerns, dependency injection, and comprehensive test suites. Target >85% code coverage for critical modules.

## 4. Architecture

### 4.1. Backend Components

1.  **FastAPI Application**: Core web server using FastAPI.
    -   Provides RESTful API endpoints defined with Pydantic models for validation.
    -   Manages WebSocket connections for real-time bidirectional communication.
    -   Includes middleware for Authentication (JWT), CORS, Security Headers, Logging, Error Handling.
2.  **Database Layer (Web UI Specific)**:
    -   SQLAlchemy ORM for interacting with a dedicated SQLite database (or potentially PostgreSQL for scalability) storing user accounts, sessions, preferences, and potentially UI-specific configurations.
    -   Alembic for managing database schema migrations.
    -   Connection pooling configured for performance.
3.  **Authentication & Authorization System**:
    -   JWT generation and validation (`python-jose`, `passlib[bcrypt]`).
    -   RBAC implementation using FastAPI dependencies or custom middleware.
    -   Secure session management.
4.  **Orchestrator Integration Layer**:
    -   Module responsible for communicating with the Legion `Orchestrator`. This likely involves:
        -   *Option A (RPC/API):* Exposing a simple control API (e.g., via ZeroMQ, gRPC, or a dedicated HTTP endpoint) on the Orchestrator process itself (requires careful security considerations due to PID lock).
        -   *Option B (Message Queue):* Using a message queue (e.g., Redis Streams, RabbitMQ) for commands (Web -> Orch) and events (Orch -> Web). This decouples the components but adds infrastructure complexity.
        -   *Option C (Direct Function Call - If applicable):* If running in the same process or environment allows, direct calls might be possible but are less scalable/robust.
    -   Handles serialization/deserialization of commands and responses.
    -   Manages state synchronization or delegates to the Orchestrator/State Manager.
5.  **Caching Layer (Optional but Recommended)**:
    -   Redis or in-memory cache (e.g., `cachetools`) for frequently accessed, non-critical data (e.g., agent list, system status).
    -   Clear cache invalidation strategies (time-based, event-based).

### 4.2. API Endpoints (Revised & Expanded)

*Base Path: `/api/v1`*

#### Authentication (`/auth`)
- `POST /login`: User login (username/password), returns JWT access/refresh tokens.
- `POST /logout`: User logout (server-side token invalidation if using refresh tokens).
- `POST /refresh`: Obtain new access token using refresh token.
- `GET /me`: Get current authenticated user's details and permissions.

#### Agents (`/agents`)
- `GET /`: List all registered agents with status and basic info.
- `GET /{agent_name}`: Get detailed status and configuration for a specific agent.
- `POST /{agent_name}/dispatch`: Send a message/command to the agent (proxied to Orchestrator).
- `GET /{agent_name}/history`: Get paginated conversation history initiated via web UI.
- `GET /{agent_name}/config`: Get current configuration for an agent.
- `PUT /{agent_name}/config`: Update agent configuration (requires Admin/AgentOperator role).
- `POST /{agent_name}/assess`: Trigger agent self-assessment (requires Admin/AgentOperator role).
- `POST /{agent_name}/start|stop|restart`: Control agent lifecycle (requires Admin/AgentOperator role).

#### System (`/system`)
- `GET /status`: Get overall system status (Orchestrator status, agent health summary).
- `GET /metrics`: Get detailed system and performance metrics.
- `GET /logs`: Get paginated and filterable system logs.
- `GET /memory/stats`: Get memory system usage statistics.
- `GET /config`: Get current system-level configuration.
- `PUT /config`: Update system-level configuration (requires Admin role).

#### Memory (`/memory`)
- `GET /agents/{agent_name}/search`: Search a specific agent's vector memory. Requires query text/embedding.
- `GET /search`: Search across all agent memories (if feasible). Requires query text/embedding.
- `GET /documents`: List available documents stored by `LegionMemory`.
- `GET /documents/{doc_name}`: Retrieve a specific document (latest version or specific version).

### 4.3. WebSocket Endpoints

- `/ws/events`: Streams real-time, filtered system events (e.g., agent status changes, errors, key metrics). Supports filtering based on client subscription.
- `/ws/agents/{agent_name}/feed`: Establishes a persistent connection for real-time updates specific to one agent (e.g., ongoing thought processes, detailed status). *Requires careful design to avoid overwhelming clients.*
- `/ws/system/metrics`: Streams key system metrics at regular intervals.

## 5. Database Schema (Web UI Specific)

*(Includes previously defined tables + enhancements)*

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL, -- Store hash (bcrypt)
    role TEXT NOT NULL DEFAULT 'viewer', -- e.g., 'admin', 'agent_operator', 'viewer'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
CREATE INDEX idx_users_username ON users (username);
CREATE INDEX idx_users_email ON users (email);
```

### Roles & Permissions Tables (Optional - for fine-grained RBAC)
```sql
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL -- e.g., 'agent:config:update', 'system:logs:read'
);

CREATE TABLE role_permissions (
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id)
);
```

### Sessions/Tokens Table (If using stateful refresh tokens)
```sql
CREATE TABLE refresh_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token_hash TEXT UNIQUE NOT NULL, -- Store hash of the refresh token
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens (user_id);
```

### Agent Configurations Table (Alternative to direct YAML modification)
*(Consider if managing config via DB is preferred over direct file edits)*
```sql
CREATE TABLE agent_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT UNIQUE NOT NULL,
    config_data TEXT NOT NULL, -- JSON blob or specific columns
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by_user_id INTEGER,
    FOREIGN KEY (updated_by_user_id) REFERENCES users(id)
);
```

### User Preferences Table
```sql
CREATE TABLE user_preferences (
    user_id INTEGER PRIMARY KEY,
    theme TEXT DEFAULT 'dark',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    -- Add other preferences as needed
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Audit Log Table
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, -- Can be NULL for system actions
    action TEXT NOT NULL, -- e.g., 'login', 'agent_config_update', 'message_sent'
    target_resource TEXT, -- e.g., 'agent:architect', 'system:config'
    details TEXT, -- JSON blob with details
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs (timestamp);
CREATE INDEX idx_audit_logs_user_id ON audit_logs (user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs (action);
```

## 6. Implementation Plan

### Phase 0: Setup & Foundation (Sprint 0/1)
1.  **Project Scaffolding**: Set up FastAPI project structure within `interface/`.
2.  **Dependency Management**: Finalize `requirements.txt` for the interface.
3.  **Tooling Setup**: Configure `ruff`, `mypy`, `pytest`, `bandit` for the `interface/` module. Add pre-commit hooks.
4.  **Database Setup**: Initialize SQLite DB and Alembic migrations for UI-specific tables (Users, Preferences).
5.  **Basic API Framework**: Implement health check endpoint (`/health`), basic error handling middleware, structured logging setup (using `legion/core/logging_config.py`).
6.  **CI Setup**: Configure CI pipeline (GitHub Actions) for linting, type checking, and basic tests for the `interface/` module.
*Deliverables*: Basic runnable FastAPI app, CI pipeline passing basic checks, DB schema initialized.*

### Phase 1: Authentication & User Management (Sprint 1/2)
1.  **Implement User Model & DB**: Create User model (SQLAlchemy), migrations.
2.  **Implement Hashing**: Integrate `passlib` for password hashing.
3.  **Implement JWT Auth**: Create login endpoint, JWT generation/validation middleware (`python-jose`).
4.  **Implement Core Auth Endpoints**: `/auth/login`, `/auth/refresh`, `/auth/me`.
5.  **Implement RBAC**: Define roles/permissions, integrate checks into endpoints (initially basic roles: Admin, Viewer).
6.  **Implement User Preferences**: API endpoints for getting/setting user preferences.
7.  **Testing**: Unit tests for auth logic, API tests for endpoints.
*Deliverables*: Secure authentication, basic RBAC, user preference management.*

### Phase 2: Core Agent & System Read Endpoints (Sprint 2/3)
1.  **Orchestrator Integration POC**: Decide and implement basic communication mechanism with Orchestrator (e.g., simple API call, MQ listener).
2.  **Implement Agent Read APIs**: `GET /api/v1/agents`, `GET /api/v1/agents/{agent_name}`, `GET /api/v1/agents/{agent_name}/config`.
3.  **Implement System Read APIs**: `GET /api/v1/system/status`, `GET /api/v1/system/metrics`, `GET /api/v1/system/logs`, `GET /api/v1/system/memory/stats`.
4.  **Implement Memory Read APIs**: `GET /api/v1/memory/agents/{agent_name}/search`, `GET /api/v1/memory/documents`.
5.  **WebSocket Foundation**: Implement basic WebSocket connection management and event broadcasting (`/ws/events`). Stream basic agent status changes.
6.  **Testing**: Integration tests for Orchestrator communication, API tests for read endpoints.
*Deliverables*: Ability to view agent/system status, logs, memory via API and basic WebSocket updates.*

### Phase 3: Agent Interaction & Configuration (Sprint 3/4)
1.  **Implement Agent Write APIs**: `POST /api/v1/agents/{agent_name}/dispatch`, `POST /api/v1/agents/{agent_name}/assess`, `POST /api/v1/agents/{agent_name}/start|stop|restart`.
2.  **Implement Agent Config API**: `PUT /api/v1/agents/{agent_name}/config`.
3.  **Implement System Config API**: `PUT /api/v1/system/config`.
4.  **Implement Conversation History**: `GET /api/v1/agents/{agent_name}/history`. Requires storing web-initiated interactions.
5.  **Enhance WebSockets**: Implement agent-specific feeds (`/ws/agents/{agent_name}/feed`) if deemed necessary. Add filtering to `/ws/events`.
6.  **Testing**: API tests for write endpoints, testing interaction flows.
*Deliverables*: Full agent interaction and configuration capabilities via API.*

### Phase 4: Frontend Development (Parallel or Subsequent Sprints)
*(High-level - requires separate detailed planning)*
1.  **Framework Setup**: Initialize React/Vue project.
2.  **Component Library**: Develop reusable UI components.
3.  **Authentication UI**: Login page, token handling.
4.  **Dashboard UI**: Implement views for agent list, system status, metrics.
5.  **Agent Interaction UI**: Chat interface, configuration forms.
6.  **Log/Memory Viewer UI**: Implement interfaces for viewing logs and memory.
7.  **WebSocket Integration**: Connect UI to WebSocket endpoints for real-time updates.
*Deliverables*: Functional web frontend consuming the backend API.*

### Phase 5: Hardening & Deployment (Sprint 5+)
1.  **Security Audit**: Perform OWASP ZAP scan, review dependencies, code audit.
2.  **Performance Testing**: Load testing API endpoints and WebSocket connections.
3.  **Refinement & Bug Fixing**: Address issues found during testing.
4.  **Documentation**: Finalize API documentation (e.g., Swagger/OpenAPI), user guides.
5.  **Deployment Setup**: Create Dockerfile, configure deployment environment (e.g., K8s manifests, server setup), update `scripts/deploy.sh` or CI/CD pipeline.
6.  **Monitoring Setup**: Integrate with Prometheus/Grafana, set up alerts.
*Deliverables*: Production-ready, tested, documented, and deployable web interface backend.*

## 7. Technology Stack

### Backend
- **Framework**: FastAPI (`^0.100+`)
- **ORM**: SQLAlchemy (`^2.0`)
- **Migrations**: Alembic (`^1.9+`)
- **Database**: SQLite (development/small scale), PostgreSQL (production/large scale)
- **Authentication**: `python-jose` (JWT), `passlib[bcrypt]` (hashing)
- **Validation**: Pydantic (inherent in FastAPI)
- **WebSockets**: FastAPI WebSockets
- **Async**: `asyncio`, `httpx` (for external calls)
- **Caching**: Redis (`redis-py`) or `cachetools` (in-memory) - *TBD*
- **Task Queue (If needed for long tasks)**: Celery with Redis/RabbitMQ - *TBD*

### Frontend (Recommendation)
- **Framework**: React (`^18.0`) with TypeScript
- **State Management**: Redux Toolkit or Zustand
- **UI Library**: Material UI (MUI) or Tailwind CSS + Headless UI
- **WebSocket Client**: `socket.io-client` or native WebSocket API
- **HTTP Client**: Axios or `fetch` API
- **Build Tool**: Vite

### DevOps
- **Containerization**: Docker
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana, Loki (for logs)
- **Logging**: Structured JSON logging (via `legion/core/logging_config.py`)
- **Infrastructure**: *TBD* (e.g., Kubernetes, Docker Compose, Serverless)

## 8. Security Considerations

*(Expanded from NFRs)*

1.  **Authentication & Authorization**:
    -   Use strong password policies enforced server-side.
    -   Implement JWTs with short-lived access tokens and longer-lived, securely stored refresh tokens. Include standard claims (`exp`, `iat`, `sub`).
    -   Enforce RBAC strictly on all relevant API endpoints using FastAPI dependencies.
2.  **Data Protection**:
    -   Enforce HTTPS via reverse proxy (e.g., Nginx, Traefik) or directly in ASGI server (e.g., Uvicorn with SSL certs).
    -   Use Pydantic for rigorous input validation against defined schemas for all API request bodies and query parameters.
    -   Sanitize all user-provided input displayed in logs or potentially used in DB queries (though ORMs help prevent SQLi).
    -   Apply appropriate security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options) via middleware.
3.  **API Security**:
    -   Implement rate limiting (e.g., `slowapi` library) on login endpoints and potentially other sensitive APIs.
    -   Configure CORS middleware precisely to allow only trusted frontend origins.
    -   Implement CSRF protection, especially if using cookie-based sessions alongside JWTs for certain operations.
4.  **Session Management**:
    -   Ensure secure handling of JWTs on the client-side (e.g., HttpOnly cookies for refresh tokens if applicable, careful local/session storage use for access tokens).
    -   Implement token revocation mechanisms for logout and security events.
5.  **Dependency Management**: Automate vulnerability scanning (Dependabot, `safety`).
6.  **Secrets Management**: Use environment variables loaded via `python-dotenv` locally and proper secrets management in deployment.
7.  **Logging & Auditing**: Implement detailed audit logs for security-sensitive actions (logins, config changes, etc.). Avoid logging sensitive data (passwords, tokens).

## 9. Performance Optimization

*(Expanded from NFRs)*

1.  **Database Optimization**:
    -   Define appropriate indexes on frequently queried columns (Usernames, Foreign Keys, Timestamps). Analyze query plans (`EXPLAIN ANALYZE`).
    -   Use efficient querying patterns (avoid N+1 queries, select only necessary columns).
    -   Configure adequate connection pooling (`SQLAlchemy`).
2.  **Caching Strategy**:
    -   Cache read-heavy, relatively static data (e.g., agent list, system config).
    -   Implement appropriate TTLs and invalidation logic (e.g., invalidate agent cache on config update).
    -   Consider Redis for distributed caching if scaling horizontally.
3.  **API Optimization**:
    -   Implement pagination for all list endpoints (`limit`/`offset` or cursor-based).
    -   Use response compression (GZip) via middleware.
    -   Leverage FastAPI's async capabilities fully. Avoid blocking I/O operations.
    -   Optimize serialization/deserialization (Pydantic is generally fast).
4.  **WebSocket Optimization**:
    -   Optimize message serialization (e.g., using `orjson`).
    -   Implement filtering/subscriptions server-side to avoid sending unnecessary data.
    -   Use efficient connection management. Consider heartbeat messages to detect stale connections.
5.  **Profiling**: Use profiling tools (e.g., `cProfile`, `Pyinstrument`, `Scalene`) during development and testing to identify bottlenecks.
6.  **Load Testing**: Use tools like `locust` or `k6` to simulate user load and identify performance limits before deployment.

## 10. Observability

1.  **Logging**:
    -   **Standard**: Utilize `legion/core/logging_config.py` for structured JSON logs across the web backend.
    -   **Correlation**: Inject a unique request/correlation ID into logs for tracing requests across services.
    -   **Levels**: Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    -   **Aggregation**: Ship logs to a central aggregator (e.g., Loki, Elasticsearch, Datadog).
2.  **Metrics**:
    -   **Exposition**: Expose key application metrics via a `/metrics` endpoint in Prometheus format (e.g., using `starlette-prometheus`).
    -   **Key Metrics**: Track request latency (histograms), request counts, error rates (per endpoint/status code), active WebSocket connections, DB connection pool usage, resource utilization (CPU/memory).
    -   **Dashboarding**: Visualize metrics in Grafana.
3.  **Tracing (Optional - Advanced)**:
    -   Implement distributed tracing using OpenTelemetry standards if interactions become complex (e.g., involving multiple microservices or complex async tasks).
    -   Trace requests across API calls, Orchestrator interactions, and database queries.

## 11. Testing Strategy

1.  **Unit Tests (`pytest`)**: Test individual functions, classes, and methods in isolation. Focus on business logic, helpers, validation. Use mocks (`unittest.mock`) extensively to isolate dependencies (DB, Orchestrator, external APIs). Aim for >80% coverage.
2.  **Integration Tests (`pytest`)**: Test interactions between components within the web backend (e.g., API endpoint -> Service Layer -> DB). Test middleware. May involve a test database.
3.  **API/Contract Tests (`pytest` with `httpx`)**: Test API endpoints from the client perspective. Verify request/response schemas, status codes, and authentication/authorization logic. Use FastAPI's `TestClient`.
4.  **End-to-End (E2E) Tests (Optional - `playwright`/`selenium`)**: Simulate user flows through the frontend interacting with the backend. Typically run less frequently.
5.  **Performance Tests (`locust`, `k6`)**: Simulate load to measure latency, throughput, and resource usage under stress.
6.  **Security Testing**: Use automated scanners (OWASP ZAP, `bandit`, `safety`) and potentially manual penetration testing.
7.  **Test Environment**: Maintain a dedicated testing environment with seeded data.
8.  **CI Integration**: Run unit, integration, and API tests automatically in the CI pipeline on every commit/PR.

## 12. Pythonic Robustness & Maintainability

*Reference: [Tips for writing robust Python code: functions](https://dev.to/uponthesky/pythontips-for-writing-robust-python-code-functions-2g2k)*

1.  **Type Annotations**: Mandatory type hints for all function signatures and key variables. Enforced by `mypy` in CI.
2.  **Keyword-Only Arguments**: Use `*` in function signatures for functions with multiple arguments (especially configuration or context parameters) to improve clarity and reduce positional errors.
3.  **Immutability & Pure Functions**: Favor pure functions (no side effects) for utilities where possible. When modifying shared state (like database objects), clearly delineate those functions (e.g., service layer methods) and minimize side effects elsewhere. Return copies instead of modifying input objects where practical.
4.  **Decorators**: Utilize decorators for cross-cutting concerns like authentication checks (`@require_role('admin')`), request timing/logging, caching, and potentially transaction management.
5.  **Clear Naming & Structure**: Adhere to Legion's naming conventions (`project_config.md`). Maintain logical module structure within `interface/`.
6.  **Docstrings**: Write clear docstrings for all public modules, classes, and functions, explaining purpose, arguments, and return values.
7.  **Accuracy and Plan Persistence Directives**: Ensure unwavering accuracy in task execution, persist with plans through incremental steps, review changes before concluding tasks, update all relevant documentation, verify component isolation, avoid unnecessary functions, check for existing files before creation, and use efficient file viewing methods as per guidelines.

## 13. Conclusion

This enhanced backend planning document provides a significantly more robust roadmap for developing the Legion web interface. It incorporates detailed requirements, a layered architecture, stringent security and performance considerations, comprehensive observability and testing strategies, and aligns with Legion's overall quality standards. Following this plan will facilitate the creation of a reliable, scalable, and maintainable backend, effectively extending the Legion system's capabilities.

## 14. Implementation Progress Update (2024-06-16)

### Agent CRUD Endpoints & Tests
- All Agent CRUD endpoints (`create`, `read`, `update`, `delete`, `list`) are now implemented in the FastAPI backend.
- Endpoints enforce correct authentication and authorization (active user for read/list, superuser for create/update/delete).
- All endpoints use the new CRUD layer (`interface/crud/crud_agent.py`), replacing the previous service layer. The `interface/services/` directory has been removed for clarity and maintainability.
- Alembic migration for the `agents` table is applied and tested.
- Comprehensive tests for all Agent CRUD endpoints are present in `tests/test_interface.py`, covering:
    - Success and failure cases
    - Permission errors (regular user vs. superuser)
    - Not found and name conflict scenarios
    - Test database isolation and dependency overrides
- The backend is now fully compliant with the legion-structure and the requirements in this planning document.

### Phase Completion reference @backend_planning.md and @changelog
