# Legion MCP Integration with Cursor IDE

This document explains how Legion's unified MCP (Model Context Protocol) system integrates with Cursor IDE for development workflows.

## Overview

Legion provides a **unified MCP system** that consolidates multiple development tools into two main MCP servers:

1. **`legion-unified`** - The core MCP server handling data operations
2. **`legion-lmstudio`** - LM Studio integration bridge

## Quick Setup

Run the automated setup script:

```bash
./scripts/setup_cursor_mcp.sh
```

This will:
- Backup your existing Cursor MCP configuration
- Install the Legion unified MCP configuration
- Set up proper file permissions
- Validate the installation

## MCP Servers

### 1. Legion Unified MCP Server

**Purpose**: Primary development data operations

**Capabilities**:
- **Vector Memory**: Store and retrieve code embeddings for semantic search
- **Cache Management**: TTL-based caching for expensive operations
- **Event Logging**: Structured logging with severity levels
- **Codebase Analysis**: File analysis and dependency tracking
- **DevOps Operations**: Deployment and monitoring operations

**Configuration**:
```json
{
  "command": "/Users/vix/Dev/Programs/Legion/scripts/start_mcp_unified.sh",
  "cwd": "/Users/vix/Dev/Programs/Legion",
  "env": {
    "MCP_SERVER_ID": "legion-unified",
    "MCP_TRANSPORT": "stdio",
    "MCP_DB_PATH": "memory/db/mcp_unified.db",
    "MCP_LOG_LEVEL": "INFO"
  }
}
```

**Available Methods**:
- `vector/store` - Store code embeddings
- `vector/retrieve` - Search similar code
- `cache/store` - Cache operation results
- `cache/get` - Retrieve cached data
- `event/log` - Log development events
- `event/get` - Query event history
- `codebase/store` - Store file analysis
- `codebase/get` - Retrieve analysis data
- `devops/log` - Log deployment operations
- `devops/update` - Update operation status
- `stats` - Performance statistics
- `health` - Health check

### 2. Legion LM Studio Bridge

**Purpose**: Local AI model integration

**Capabilities**:
- **Chat Completions**: Direct OpenAI-compatible API access
- **Model Discovery**: List available models
- **Raw Generation**: Custom generation requests
- **Health Monitoring**: LM Studio status checks

**Configuration**:
```json
{
  "command": "/Users/vix/Dev/Programs/Legion/.venv/bin/python",
  "args": ["-m", "legion.mcp.bridges.lmstudio_bridge"],
  "cwd": "/Users/vix/Dev/Programs/Legion",
  "env": {
    "MCP_SERVER_ID": "legion-lmstudio",
    "MCP_TRANSPORT": "stdio",
    "LMSTUDIO_BASE_URL": "http://127.0.0.1:1234/v1"
  }
}
```

**Available Methods**:
- `chat/completions` - Chat with local models
- `models/discover` - List available models
- `generate` - Raw text generation
- `stats` - LM Studio status

## Development Workflows

### 1. Code Analysis & Memory

Use vector memory to store and retrieve code context:

```python
# Store code analysis
await mcp_server.store_vector_memory(
    agent_name="developer",
    text="Function implementation for user authentication",
    embedding=code_embedding,
    metadata={"file": "auth.py", "function": "authenticate_user"}
)

# Retrieve similar code
similar_code = await mcp_server.retrieve_vector_memory(
    agent_name="developer",
    query_embedding=query_embedding,
    top_k=5
)
```

### 2. Caching Expensive Operations

Cache build results, test outputs, or API responses:

```python
# Cache build results
await mcp_server.store_cache(
    agent_name="developer",
    key="build_result_v1.2.3",
    value=build_output,
    ttl_seconds=3600  # 1 hour
)

# Retrieve cached results
cached_result = await mcp_server.get_cache("build_result_v1.2.3")
```

### 3. Development Event Logging

Track development activities and debugging:

```python
# Log debugging events
await mcp_server.log_event(
    agent_name="developer",
    event_type="debug_session",
    event_data={
        "file": "main.py",
        "line": 42,
        "issue": "Unexpected None value",
        "solution": "Added null check"
    },
    severity="info"
)
```

### 4. LM Studio Integration

Direct access to local AI models:

```python
# Chat with local model
response = await lm_studio.chat_complete(
    messages=[
        {"role": "user", "content": "Explain this code snippet"}
    ],
    model="llama-3.1-8b-instruct"
)
```

## Configuration Details

### Environment Variables

**Unified MCP Server**:
- `MCP_DB_PATH` - Database file path (default: `memory/db/mcp_unified.db`)
- `MCP_LOG_LEVEL` - Logging level (default: `INFO`)
- `MCP_CONNECTION_POOL_SIZE` - DB connection pool size
- `MCP_DEFAULT_CACHE_TTL` - Default cache TTL in seconds

**LM Studio Bridge**:
- `LMSTUDIO_BASE_URL` - LM Studio API endpoint
- `OPENAI_API_BASE` - OpenAI-compatible base URL

### File Structure

```
Legion/
├── scripts/
│   ├── start_mcp_unified.sh      # Unified MCP server launcher
│   └── setup_cursor_mcp.sh       # Cursor configuration script
├── core/
│   ├── mcp_server.py             # Unified MCP server implementation
│   ├── mcp_unified.py            # Unified database layer
│   └── mcp_server/__main__.py    # CLI interface
├── legion/mcp/bridges/
│   ├── lmstudio_bridge.py        # LM Studio integration
│   └── __main__.py               # LM Studio CLI interface
├── memory/db/
│   └── mcp_unified.db            # SQLite database
└── cursor_mcp_unified.json       # Cursor MCP configuration
```

## Troubleshooting

### Common Issues

1. **MCP Server Won't Start**
   - Check virtual environment is activated
   - Verify file permissions: `chmod +x scripts/start_mcp_unified.sh`
   - Check database directory exists: `mkdir -p memory/db/`

2. **Cursor Can't Connect**
   - Restart Cursor IDE after configuration changes
   - Check MCP server logs in Cursor developer console
   - Verify working directory path in configuration

3. **LM Studio Bridge Fails**
   - Ensure LM Studio is running on `http://127.0.0.1:1234`
   - Check model is loaded in LM Studio
   - Verify API endpoint is accessible

### Debugging

Enable debug logging:
```bash
export MCP_LOG_LEVEL=DEBUG
```

Check MCP server startup manually:
```bash
cd /Users/vix/Dev/Programs/Legion
./scripts/start_mcp_unified.sh
```

Monitor database operations:
```bash
.venv/bin/python -c "
import asyncio
from core.mcp_server import get_mcp_server
async def test():
    server = await get_mcp_server()
    stats = await server.get_performance_stats()
    print('Stats:', stats)
asyncio.run(test())
"
```

## Integration with Legion Orchestrator

The MCP servers are designed for **development use** with Cursor but can be integrated into Legion's orchestration system for agent skill usage:

```python
# In agent skills
async def search_code_memory(query: str) -> List[Dict]:
    """Search code memory using MCP server."""
    mcp_server = await get_mcp_server()
    return await mcp_server.retrieve_vector_memory(
        agent_name="researcher",
        query_embedding=embed_query(query)
    )
```

This provides a bridge between development tooling and agent capabilities while maintaining clear separation of concerns.

## Performance Considerations

- **Connection Pooling**: Configurable pool size for concurrent operations
- **Cache TTL**: Automatic cleanup of expired cache entries
- **Database Optimization**: Proper indexing for vector similarity searches
- **Background Tasks**: Async cleanup and monitoring tasks

The unified system is designed for production-scale development workflows while maintaining simplicity for individual developer use.
