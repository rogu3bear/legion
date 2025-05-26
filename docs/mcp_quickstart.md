# Legion MCP Quick Start Guide

Get Legion's MCP tools working with Cursor IDE in under 2 minutes.

## Prerequisites
- ✅ Legion repository cloned
- ✅ Virtual environment activated (`.venv` or `venv`)
- ✅ Dependencies installed (`pip install -r requirements.txt`)
- ✅ Cursor IDE installed

## One-Command Setup

```bash
./scripts/setup_cursor_mcp.sh
```

This script:
1. 📦 Backs up your existing Cursor MCP config
2. 🚀 Installs Legion unified MCP configuration
3. ✅ Sets proper file permissions
4. 🧪 Validates the setup

## Verify Installation

```bash
# Test MCP servers respond correctly
python scripts/test_mcp_setup.py
```

## What You Get

After setup, Cursor's AI assistant can:
- 🧠 **Store/retrieve contextual memories** with vector embeddings
- 💾 **Cache data** with automatic expiration
- 📝 **Log development events** by severity and type
- 🔍 **Analyze codebase** with change detection
- ⚙️ **Monitor DevOps operations**

## Usage in Cursor

1. **Restart Cursor IDE** after setup
2. **Chat with AI** and mention using MCP tools:
   - "Store this analysis in vector memory"
   - "Cache this API response for an hour"
   - "Log this as a high-severity event"
   - "Analyze the current codebase structure"

## Troubleshooting

### Problem: "MCP server not found"
**Solution:**
```bash
# Ensure script is executable
chmod +x scripts/start_mcp_unified.sh

# Check virtual environment
source .venv/bin/activate  # or source venv/bin/activate
```

### Problem: "Import errors"
**Solution:**
```bash
# Install/reinstall dependencies
pip install -r requirements.txt

# Ensure core module is a package
touch core/__init__.py
```

### Problem: "Cursor not detecting MCP"
**Solution:**
- Restart Cursor IDE completely
- Check `~/.cursor/mcp.json` exists
- Monitor Cursor developer console for MCP logs

## Advanced

**Configuration file:** `~/.cursor/mcp.json`
**Database:** `memory/db/mcp_unified.db`
**Detailed docs:** [mcp_cursor_integration.md](mcp_cursor_integration.md)

## Health Check

```bash
# Quick health test
echo '{"jsonrpc": "2.0", "method": "health", "id": 1}' | ./scripts/start_mcp_unified.sh
# Expected: {"jsonrpc": "2.0", "result": {"status": "healthy", ...}, "id": 1}
```
