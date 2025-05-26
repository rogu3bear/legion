#!/usr/bin/env bash
# Setup Cursor IDE with Legion Unified MCP Configuration
# This script updates Cursor's MCP configuration to use Legion's unified MCP system

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Cursor MCP configuration path
CURSOR_MCP_CONFIG="$HOME/.cursor/mcp.json"
BACKUP_CONFIG="$PROJECT_ROOT/backup/mcp_migration/cursor_mcp_backup_$(date +%Y%m%d_%H%M%S).json"

echo "🔧 Setting up Cursor IDE with Legion Unified MCP..."

# Create backup directory if it doesn't exist
mkdir -p "$(dirname "$BACKUP_CONFIG")"

# Backup existing Cursor MCP config if it exists
if [ -f "$CURSOR_MCP_CONFIG" ]; then
    echo "📦 Backing up existing Cursor MCP config to: $BACKUP_CONFIG"
    cp "$CURSOR_MCP_CONFIG" "$BACKUP_CONFIG"
else
    echo "ℹ️  No existing Cursor MCP config found"
fi

# Ensure Cursor config directory exists
mkdir -p "$(dirname "$CURSOR_MCP_CONFIG")"

# Copy the new unified MCP configuration
echo "🚀 Installing Legion Unified MCP configuration..."
cp "$PROJECT_ROOT/cursor_mcp_unified.json" "$CURSOR_MCP_CONFIG"

# Make the startup script executable
chmod +x "$PROJECT_ROOT/scripts/start_mcp_unified.sh"

echo "✅ Cursor MCP configuration updated successfully!"
echo ""
echo "📋 Configuration Details:"
echo "  • Unified MCP Server: legion-unified"
echo "  • LM Studio Bridge: legion-lmstudio"
echo "  • Database: memory/db/mcp_unified.db"
echo "  • Working Directory: $PROJECT_ROOT"
echo ""
echo "🔄 Next steps:"
echo "  1. Restart Cursor IDE to apply the new MCP configuration"
echo "  2. The unified MCP server will automatically start when Cursor loads"
echo "  3. Use MCP tools in Cursor for:"
echo "     - Vector memory operations"
echo "     - Cache management"
echo "     - Event logging"
echo "     - Codebase analysis"
echo "     - DevOps operations"
echo "     - LM Studio integration"
echo ""
echo "🧪 Test the configuration:"
echo "  • Check Cursor's MCP status in the IDE"
echo "  • Try using MCP tools in a conversation"
echo "  • Monitor logs in the Cursor developer console"

# Test if the startup script can be executed
echo ""
echo "🔍 Testing MCP startup script..."
if [ -x "$PROJECT_ROOT/scripts/start_mcp_unified.sh" ]; then
    echo "✅ MCP startup script is executable"
else
    echo "❌ Error: MCP startup script is not executable"
    echo "   Run: chmod +x $PROJECT_ROOT/scripts/start_mcp_unified.sh"
fi

# Test if virtual environment exists
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo "✅ Virtual environment found at $PROJECT_ROOT/.venv"
elif [ -d "$PROJECT_ROOT/venv" ]; then
    echo "✅ Virtual environment found at $PROJECT_ROOT/venv"
else
    echo "⚠️  Warning: No virtual environment found"
    echo "   Consider creating one: python -m venv .venv"
fi

echo ""
echo "🎉 Legion MCP setup for Cursor IDE complete!"
echo "   Configuration file: $CURSOR_MCP_CONFIG"
