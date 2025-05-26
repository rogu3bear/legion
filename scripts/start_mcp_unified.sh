#!/usr/bin/env bash
# Unified MCP Server for Legion - Cursor IDE Compatible
# Starts the unified MCP server for development use with Cursor

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_ROOT" || {
    echo "Error: Could not change to project directory: $PROJECT_ROOT" >&2
    exit 1
}

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "Activated .venv virtual environment" >&2
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo "Activated venv virtual environment" >&2
else
    echo "Warning: No virtual environment found (.venv or venv)" >&2
fi

# Set environment variables for MCP
export MCP_SERVER_TYPE="unified"
export MCP_DB_PATH="memory/db/mcp_unified.db"
export MCP_LOG_LEVEL="${MCP_LOG_LEVEL:-INFO}"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Ensure database directory exists
mkdir -p "$(dirname "$MCP_DB_PATH")"

# Start the unified MCP server
echo "Starting Legion Unified MCP Server..." >&2
echo "Database: $MCP_DB_PATH" >&2
echo "Log Level: $MCP_LOG_LEVEL" >&2

# Run the unified MCP server
exec python -m core.mcp_server
