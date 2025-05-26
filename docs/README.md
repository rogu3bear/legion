# Legion Documentation

<!-- Note: Default dev port changed from 8000 to 27001 to avoid conflicts -->

This directory centralizes architecture and system documentation.

## Quick Start

### WebUI Access

The Legion WebUI now requires authentication. To access the prompt management interface:

1. Start the Legion interface server:
   ```bash
   uvicorn interface.main:app --host 127.0.0.1 --port 27001
   ```

2. Navigate to `http://localhost:27001/prompts`

3. Login with demo credentials:
   - **Username:** `testuser`
   - **Password:** `test123`

4. You can now:
   - Edit agent prompts
   - Test prompts with LM Studio
   - Create new agent configurations

### Creating Additional Users

To create additional users for testing, use the registration API endpoint at `/api/v1/auth/register`.

## Deployment Profiles & Port Map

Legion supports multiple deployment environments with different configurations:

### Development Profile (`.env.development`)
- **DEBUG**: `true` (enabled)
- **Ports**: 27000-27999 range
- **Features**: Hot reload, detailed logging, development middleware

### Staging Profile (`.env`)
- **DEBUG**: `false` (disabled)
- **Ports**: Dynamic allocation
- **Features**: Production-like configuration with debug disabled

### Production Profile (`.env.production`)
- **DEBUG**: `false` (disabled)
- **Ports**: 31000-31999 cluster range
- **Features**: Optimized for production deployment, cluster-safe ports

### Port Allocation Map

| Service | Dev | Staging | Production |
|---------|-----|---------|------------|
| Web UI | 27000-27999 | Dynamic | 31001 |
| Orchestrator | 27000-27999 | Dynamic | 31000 |
| ChromaDB | 27000-27999 | Dynamic | 31020 |
| Prometheus | 27000-27999 | Dynamic | 31030 |
| Redis | 27000-27999 | Dynamic | 31040 |
| PostgreSQL | 27000-27999 | Dynamic | 31050 |

See [Port Map](architecture/ports.md) for detailed port configuration.

## Documentation Index

### Core Documentation
- [Architecture Overview](architecture/overview.md)
- [Port Map](architecture/ports.md)
- [Architecture Diagrams](architecture/)
- [Agents](agents/index.md)
- [System Startup](system/startup.md)
- [Queue Protocol](system/queue_protocol.md)
- [State Schema](system/state_schema.md)
- [Project Configuration](system/config.md)
- [Dependencies](system/dependencies.md)

### Development Integration
- [MCP Quick Start](mcp_quickstart.md) - **2-minute setup** for Legion MCP tools with Cursor IDE
- [MCP Cursor Integration](mcp_cursor_integration.md) - Detailed MCP setup and configuration guide
- [WebUI Guide](webui.md) - Web interface documentation
- [LM Studio Integration](llm/local-lmstudio.md) - Local LLM inference setup
- [Security Guidelines](security.md) - Security best practices
