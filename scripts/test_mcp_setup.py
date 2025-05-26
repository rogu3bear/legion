#!/usr/bin/env python3
"""
Test script for Legion MCP setup verification
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_unified_mcp():
    """Test the unified MCP server functionality."""
    logger.info("Testing Legion Unified MCP Server...")

    try:
        # Import directly from the mcp_server.py file
        import importlib.util
        mcp_server_path = project_root / "core" / "mcp_server.py"
        spec = importlib.util.spec_from_file_location("mcp_server_module", mcp_server_path)
        mcp_server_module = importlib.util.module_from_spec(spec)

        # Add core to path for dependencies
        sys.path.insert(0, str(project_root / "core"))
        spec.loader.exec_module(mcp_server_module)

        get_mcp_server = mcp_server_module.get_mcp_server

        # Initialize MCP server
        mcp_server = await get_mcp_server()
        logger.info("✅ MCP server initialized successfully")

        # Test health check
        health = await mcp_server.health_check()
        logger.info(f"✅ Health check: {health['status']}")

        # Test performance stats
        stats = await mcp_server.get_performance_stats()
        logger.info(f"✅ Performance stats: {stats['total_operations']} operations")

        # Test cache operations
        cache_id = await mcp_server.store_cache(
            agent_name="test", key="test_key", value={"test": "data"}, ttl_seconds=300
        )
        logger.info(f"✅ Cache store test: {cache_id}")

        cached_value = await mcp_server.get_cache("test_key")
        if cached_value:
            logger.info("✅ Cache retrieve test passed")
        else:
            logger.warning("⚠️ Cache retrieve test failed")

        # Test event logging
        event_id = await mcp_server.log_event(
            agent_name="test",
            event_type="test_event",
            event_data={"test": "event_data"},
            severity="info",
        )
        logger.info(f"✅ Event logging test: {event_id}")

        # Cleanup
        await mcp_server.shutdown()
        logger.info("✅ MCP server shutdown successfully")

        return True

    except Exception as e:
        logger.error(f"❌ Unified MCP test failed: {e}")
        return False


async def test_lmstudio_bridge():
    """LM Studio bridge was removed from the MCP architecture."""
    logger.info("LM Studio bridge was removed - no longer part of MCP architecture")
    logger.info("ℹ️ MCP servers should provide tools TO AI models, not call other AI models")
    return True  # Always pass since it's intentionally removed


def test_cursor_config():
    """Test Cursor MCP configuration."""
    logger.info("Testing Cursor MCP configuration...")

    cursor_config_path = Path.home() / ".cursor" / "mcp.json"

    if not cursor_config_path.exists():
        logger.error("❌ Cursor MCP configuration not found")
        return False

    try:
        with open(cursor_config_path) as f:
            config = json.load(f)

        servers = config.get("mcpServers", {})

        if "legion-unified" in servers:
            logger.info("✅ Legion unified MCP server configured")
        else:
            logger.error("❌ Legion unified MCP server not configured")
            return False

        # LM Studio bridge intentionally removed from MCP architecture
        logger.info("ℹ️ LM Studio bridge removed - MCP servers should provide tools TO models")

        # Check script paths
        unified_script = servers["legion-unified"]["command"]
        if Path(unified_script).exists():
            logger.info("✅ Unified MCP script exists")
        else:
            logger.error(f"❌ Unified MCP script not found: {unified_script}")
            return False

        # LM Studio bridge removed - skip venv check for it

        return True

    except Exception as e:
        logger.error(f"❌ Cursor config test failed: {e}")
        return False


def test_file_structure():
    """Test required file structure."""
    logger.info("Testing file structure...")

    required_files = [
        "scripts/start_mcp_unified.sh",
        "scripts/setup_cursor_mcp.sh",
        "core/mcp_server.py",
        "core/mcp_unified.py",
        "core/mcp_server/__main__.py",
        # "legion/mcp/bridges/lmstudio_bridge.py",  # Removed - not part of MCP architecture
        # "legion/mcp/bridges/__main__.py",        # Removed - not part of MCP architecture
        "cursor_mcp_unified.json.template",
        "mcp_config.json",
    ]

    all_good = True

    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            logger.info(f"✅ {file_path}")
        else:
            logger.error(f"❌ Missing: {file_path}")
            all_good = False

    # Check if scripts are executable
    scripts = ["scripts/start_mcp_unified.sh", "scripts/setup_cursor_mcp.sh"]

    for script in scripts:
        script_path = project_root / script
        if script_path.exists() and os.access(script_path, os.X_OK):
            logger.info(f"✅ {script} is executable")
        else:
            logger.error(f"❌ {script} is not executable")
            all_good = False

    # Check database directory
    db_dir = project_root / "memory" / "db"
    if db_dir.exists():
        logger.info("✅ Database directory exists")
    else:
        logger.info("ℹ️ Database directory will be created on first run")

    return all_good


async def main():
    """Run all MCP setup tests."""
    logger.info("🧪 Legion MCP Setup Verification")
    logger.info("=" * 50)

    # Test file structure
    file_test = test_file_structure()

    # Test Cursor configuration
    cursor_test = test_cursor_config()

    # Test unified MCP server
    unified_test = await test_unified_mcp()

    # Test LM Studio bridge
    lmstudio_test = await test_lmstudio_bridge()

    # Summary
    logger.info("=" * 50)
    logger.info("📊 Test Results Summary:")
    logger.info(f"  File Structure: {'✅ PASS' if file_test else '❌ FAIL'}")
    logger.info(f"  Cursor Config:  {'✅ PASS' if cursor_test else '❌ FAIL'}")
    logger.info(f"  Unified MCP:    {'✅ PASS' if unified_test else '❌ FAIL'}")
    logger.info(f"  LM Studio:      {'✅ PASS' if lmstudio_test else '❌ FAIL'}")

    all_passed = all([file_test, cursor_test, unified_test, lmstudio_test])

    if all_passed:
        logger.info("🎉 All tests passed! Legion MCP setup is ready for Cursor IDE.")
        logger.info("📝 Next steps:")
        logger.info("  1. Restart Cursor IDE to load the new MCP configuration")
        logger.info("  2. Open a conversation in Cursor and try using MCP tools")
        logger.info("  3. Check Cursor's developer console for MCP server logs")
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        logger.info(
            "🔧 Run './scripts/setup_cursor_mcp.sh' to fix configuration issues"
        )

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
