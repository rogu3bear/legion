#!/usr/bin/env python3
"""
Wrapper script for Legion Unified MCP Server
"""

import sys
from pathlib import Path

# Add project root and core directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))

# Import and run the MCP server directly
import importlib.util

main_path = project_root / "core" / "mcp_server" / "__main__.py"
spec = importlib.util.spec_from_file_location("mcp_main", main_path)
mcp_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_main)

main = mcp_main.main

if __name__ == "__main__":
    main()
