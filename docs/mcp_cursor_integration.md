# Legion MCP Integration with Cursor IDE

This document explains how Legion's unified MCP (Model Context Protocol) system integrates with Cursor IDE for development workflows.

## Overview

Legion provides a **unified MCP system** that gives Cursor IDE's AI assistant access to powerful development tools:

1. **`legion-unified`** - The core MCP server providing development tools

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

## MCP Server

### Legion Unified MCP Server

**Purpose**: Provides development tools to Cursor's AI assistant

**Capabilities**:
- **Vector Memory**: Store and retrieve contextual information with embeddings
- **Smart Caching**: Persistent key-value storage with TTL expiration
- **Event Logging**: Track and query development activities by severity/type
- **Codebase Analysis**: Store analysis results with automatic change detection
- **DevOps Operations**: Monitor and log development operations

**JSON-RPC Methods**:
- `health` - Check server health status
- `stats` - Get performance statistics
- `vector/store` - Store vector memory with embeddings
- `vector/retrieve` - Retrieve similar vectors
- `cache/store` - Store cached data with TTL
- `cache/get` - Retrieve cached data
- `event/log` - Log development events
- `event/get` - Query logged events
- `codebase/store` - Store codebase analysis
- `codebase/get` - Retrieve codebase analysis
- `devops/log` - Log DevOps operations
- `devops/update` - Update operation status

## Architecture

```
Cursor IDE (with AI assistant)
    ↓ (uses MCP tools)
Legion Unified MCP Server
    ↓ (provides)
Development Tools: memory, caching, logging, analysis
```

## Configuration Files

### Cursor MCP Configuration
Location: `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "legion-unified": {
      "command": "/Users/vix/Dev/Programs/Legion/scripts/start_mcp_unified.sh",
      "args": [],
      "cwd": "/Users/vix/Dev/Programs/Legion",
      "env": {
        "MCP_SERVER_ID": "legion-unified",
        "MCP_TRANSPORT": "stdio",
        "MCP_DB_PATH": "memory/db/mcp_unified.db",
        "MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Testing

### Manual Testing
```bash
# Test health check
echo '{"jsonrpc": "2.0", "method": "health", "id": 1}' | ./scripts/start_mcp_unified.sh

# Test statistics
echo '{"jsonrpc": "2.0", "method": "stats", "id": 1}' | ./scripts/start_mcp_unified.sh
```

### Automated Testing
```bash
# Run comprehensive test suite
python scripts/test_mcp_setup.py
```

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Check virtual environment: `source .venv/bin/activate`
   - Verify permissions: `chmod +x scripts/start_mcp_unified.sh`
   - Check database directory: `mkdir -p memory/db`

2. **Import errors**
   - Ensure all dependencies installed: `pip install -r requirements.txt`
   - Check Python path in virtual environment

3. **Cursor not detecting MCP**
   - Restart Cursor IDE after configuration changes
   - Check Cursor developer console for MCP logs
   - Verify configuration at `~/.cursor/mcp.json`

### Logs and Debugging

- **MCP Server Logs**: Sent to stderr during startup
- **Database**: SQLite at `memory/db/mcp_unified.db`
- **Configuration**: `mcp_config.json`

## Integration with LM Studio

**Note**: LM Studio integration is handled separately from MCP. LM Studio serves as the inference backend for Legion agents, not as an MCP server. The architecture is:

- **LM Studio**: Provides local LLM inference
- **Legion Agents**: Use LM Studio API for completions
- **Legion MCP Server**: Provides tools to any AI assistant (including Cursor)

This separation maintains clean architecture where:
- MCP servers provide **tools and capabilities**
- LLM servers provide **inference and completions**
