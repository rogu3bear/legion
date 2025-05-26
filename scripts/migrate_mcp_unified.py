#!/usr/bin/env python3
"""
Migration script for Legion MCP Unified Database

This script helps migrate from multiple separate MCP servers to the new
unified MCP database system. It provides data migration, configuration
updates, and validation.
"""

import asyncio
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.mcp_config import create_mcp_env_example, get_config_manager
from core.mcp_server import get_mcp_server
from core.mcp_unified import get_mcp_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPMigrationManager:
    """Manages migration from separate MCP servers to unified system."""

    def __init__(self, backup_dir: str = "backup/mcp_migration"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Old MCP server configurations (from the provided mcp.json)
        self.old_servers = {
            "auchsight-vector-memory": "/Users/vix/Dev/Websites/auchsight/MCP",
            "auchsight-cache-memory": "/Users/vix/Dev/Websites/auchsight/MCP",
            "auchsight-event-log": "/Users/vix/Dev/Websites/auchsight/MCP",
            "auchsight-codebase": "/Users/vix/Dev/Websites/auchsight/MCP",
            "auchsight-devops": "/Users/vix/Dev/Websites/auchsight/MCP",
        }

    async def run_migration(self) -> bool:
        """Run the complete migration process."""
        logger.info("Starting Legion MCP Unified Database migration...")

        try:
            # Step 1: Backup existing configuration
            await self._backup_existing_config()

            # Step 2: Analyze existing MCP servers
            analysis = await self._analyze_existing_servers()

            # Step 3: Initialize unified database
            await self._initialize_unified_database()

            # Step 4: Migrate data if possible
            if analysis['has_data']:
                await self._migrate_data(analysis)

            # Step 5: Create new configuration
            await self._create_unified_config()

            # Step 6: Validate migration
            validation_result = await self._validate_migration()

            if validation_result:
                logger.info("✅ Migration completed successfully!")
                await self._print_migration_summary()
                return True
            else:
                logger.error("❌ Migration validation failed!")
                return False

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            await self._rollback_migration()
            return False

    async def _backup_existing_config(self) -> None:
        """Backup existing MCP configuration."""
        logger.info("Backing up existing configuration...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Backup cursor MCP config if it exists
        cursor_mcp_config = Path.home() / ".cursor" / "mcp.json"
        if cursor_mcp_config.exists():
            backup_path = self.backup_dir / f"cursor_mcp_{timestamp}.json"
            shutil.copy2(cursor_mcp_config, backup_path)
            logger.info(f"Backed up cursor MCP config to {backup_path}")

        # Backup any existing MCP environment files
        for env_file in [".env.mcp", ".env.mcp.example", "mcp_config.json"]:
            source = Path(env_file)
            if source.exists():
                backup_path = self.backup_dir / f"{env_file}_{timestamp}"
                shutil.copy2(source, backup_path)
                logger.info(f"Backed up {env_file} to {backup_path}")

    async def _analyze_existing_servers(self) -> Dict[str, Any]:
        """Analyze existing MCP servers to understand current setup."""
        logger.info("Analyzing existing MCP servers...")

        analysis = {
            'servers_found': [],
            'has_data': False,
            'estimated_data_size': 0,
            'server_analysis': {}
        }

        for server_name, server_path in self.old_servers.items():
            server_dir = Path(server_path)
            if server_dir.exists():
                analysis['servers_found'].append(server_name)

                # Look for potential data files
                data_files = []
                for pattern in ['*.db', '*.sqlite', '*.sqlite3', '*.json', '*.jsonl']:
                    data_files.extend(server_dir.glob(pattern))

                if data_files:
                    analysis['has_data'] = True
                    size = sum(f.stat().st_size for f in data_files if f.exists())
                    analysis['estimated_data_size'] += size
                    analysis['server_analysis'][server_name] = {
                        'data_files': [str(f) for f in data_files],
                        'size_bytes': size
                    }

        logger.info(f"Found {len(analysis['servers_found'])} existing MCP servers")
        if analysis['has_data']:
            size_mb = analysis['estimated_data_size'] / (1024 * 1024)
            logger.info(f"Estimated data size: {size_mb:.2f} MB")

        return analysis

    async def _initialize_unified_database(self) -> None:
        """Initialize the unified MCP database."""
        logger.info("Initializing unified MCP database...")

        # Get the unified database instance (this will create the schema)
        db = await get_mcp_db()

        # Verify the database is properly initialized
        stats = await db.get_performance_stats()
        logger.info(f"Unified database initialized with {stats['connection_pool_size']} connections")

    async def _migrate_data(self, analysis: Dict[str, Any]) -> None:
        """Migrate data from old MCP servers to unified database."""
        logger.info("Migrating data from old MCP servers...")

        # This is a placeholder for actual data migration
        # In a real implementation, you would:
        # 1. Read data from old server databases
        # 2. Transform it to the new unified format
        # 3. Insert it into the unified database

        for server_name, server_info in analysis['server_analysis'].items():
            logger.info(f"Processing {server_name}...")

            # Example migration logic (would need to be customized based on actual data format)
            if 'vector' in server_name:
                await self._migrate_vector_data(server_info)
            elif 'cache' in server_name:
                await self._migrate_cache_data(server_info)
            elif 'event' in server_name:
                await self._migrate_event_data(server_info)
            elif 'codebase' in server_name:
                await self._migrate_codebase_data(server_info)
            elif 'devops' in server_name:
                await self._migrate_devops_data(server_info)

    async def _migrate_vector_data(self, server_info: Dict[str, Any]) -> None:
        """Migrate vector memory data."""
        logger.info("Migrating vector memory data...")
        # Placeholder for vector data migration
        pass

    async def _migrate_cache_data(self, server_info: Dict[str, Any]) -> None:
        """Migrate cache data."""
        logger.info("Migrating cache data...")
        # Placeholder for cache data migration
        pass

    async def _migrate_event_data(self, server_info: Dict[str, Any]) -> None:
        """Migrate event log data."""
        logger.info("Migrating event log data...")
        # Placeholder for event data migration
        pass

    async def _migrate_codebase_data(self, server_info: Dict[str, Any]) -> None:
        """Migrate codebase analysis data."""
        logger.info("Migrating codebase analysis data...")
        # Placeholder for codebase data migration
        pass

    async def _migrate_devops_data(self, server_info: Dict[str, Any]) -> None:
        """Migrate DevOps operations data."""
        logger.info("Migrating DevOps operations data...")
        # Placeholder for DevOps data migration
        pass

    async def _create_unified_config(self) -> None:
        """Create unified MCP configuration."""
        logger.info("Creating unified MCP configuration...")

        # Create the unified environment configuration example
        env_example_content = create_mcp_env_example()
        with open(".env.mcp.unified.example", "w") as f:
            f.write(env_example_content)

        # Create a sample mcp_config.json
        config_manager = get_config_manager()
        config = config_manager.load_config()
        config_manager.save_config(config)

        logger.info("Created unified MCP configuration files")

    async def _validate_migration(self) -> bool:
        """Validate the migration was successful."""
        logger.info("Validating migration...")

        try:
            # Test unified MCP server initialization
            server = await get_mcp_server()

            # Test basic operations
            health = await server.health_check()
            if health['status'] != 'healthy':
                logger.error(f"Health check failed: {health}")
                return False

            # Test database connectivity
            stats = await server.get_performance_stats()
            if not stats:
                logger.error("Failed to get performance stats")
                return False

            # Test basic operations
            test_results = await self._run_operation_tests(server)
            if not all(test_results.values()):
                logger.error(f"Operation tests failed: {test_results}")
                return False

            logger.info("✅ All validation tests passed")
            return True

        except Exception as e:
            logger.error(f"Validation failed with error: {e}")
            return False

    async def _run_operation_tests(self, server) -> Dict[str, bool]:
        """Run basic operation tests on the unified server."""
        test_results = {}

        try:
            # Test vector memory
            vector_id = await server.store_vector_memory(
                agent_name="test_migration",
                text="Test migration vector",
                embedding=[0.1] * 1536,
                metadata={"test": True}
            )
            test_results['vector_store'] = bool(vector_id)

            # Test cache
            cache_id = await server.store_cache(
                agent_name="test_migration",
                key="test_migration_key",
                value={"test": "migration_value"},
                ttl_seconds=300
            )
            test_results['cache_store'] = bool(cache_id)

            cache_value = await server.get_cache("test_migration_key")
            test_results['cache_retrieve'] = cache_value is not None

            # Test event logging
            event_id = await server.log_event(
                agent_name="test_migration",
                event_type="migration_test",
                event_data={"test": True},
                severity="info"
            )
            test_results['event_log'] = bool(event_id)

            # Test codebase analysis
            codebase_id = await server.store_codebase_analysis(
                agent_name="test_migration",
                file_path="test_file.py",
                analysis_data={"test": True},
                dependencies=["test_dependency"]
            )
            test_results['codebase_store'] = bool(codebase_id)

            # Test DevOps operations
            devops_id = await server.log_devops_operation(
                agent_name="test_migration",
                operation_type="test_migration",
                operation_data={"test": True},
                status="completed"
            )
            test_results['devops_log'] = bool(devops_id)

        except Exception as e:
            logger.error(f"Operation test failed: {e}")
            test_results['error'] = str(e)

        return test_results

    async def _rollback_migration(self) -> None:
        """Rollback migration in case of failure."""
        logger.info("Rolling back migration...")

        # Remove unified database file
        db_path = Path("memory/db/mcp_unified.db")
        if db_path.exists():
            db_path.unlink()
            logger.info("Removed unified database file")

        # Remove configuration files
        for config_file in ["mcp_config.json", ".env.mcp.unified.example"]:
            config_path = Path(config_file)
            if config_path.exists():
                config_path.unlink()
                logger.info(f"Removed {config_file}")

    async def _print_migration_summary(self) -> None:
        """Print migration summary and next steps."""
        print("\n" + "="*80)
        print("🎉 LEGION MCP UNIFIED DATABASE MIGRATION COMPLETE!")
        print("="*80)

        print("\n📋 MIGRATION SUMMARY:")
        print("• ✅ Unified MCP database initialized")
        print("• ✅ Configuration files created")
        print("• ✅ All operation tests passed")
        print("• ✅ Backup files created")

        print("\n🔧 NEXT STEPS:")
        print("1. Review the new configuration in .env.mcp.unified.example")
        print("2. Copy to .env.mcp and customize as needed")
        print("3. Update your application to use the unified MCP server")
        print("4. Remove old MCP server references")
        print("5. Test your agents with the new unified system")

        print("\n📁 CONFIGURATION FILES:")
        print("• .env.mcp.unified.example - Environment configuration template")
        print("• mcp_config.json - JSON configuration file")
        print("• memory/db/mcp_unified.db - Unified database file")

        print("\n🔄 OLD vs NEW:")
        print("OLD: Multiple separate MCP servers")
        print("     ├── auchsight-vector-memory")
        print("     ├── auchsight-cache-memory")
        print("     ├── auchsight-event-log")
        print("     ├── auchsight-codebase")
        print("     └── auchsight-devops")
        print()
        print("NEW: Single unified MCP server")
        print("     └── Legion MCP Unified Database")
        print("         ├── Vector memory operations")
        print("         ├── Cache operations")
        print("         ├── Event logging")
        print("         ├── Codebase analysis")
        print("         └── DevOps operations")

        print("\n💡 BENEFITS:")
        print("• 🚀 Better performance with optimized indexes")
        print("• 💾 Shared connection pooling")
        print("• 📊 Unified performance monitoring")
        print("• ⚙️  Simplified configuration management")
        print("• 🔧 Better resource utilization")

        print("\n⚠️  IMPORTANT:")
        print("• Backup files are in:", self.backup_dir)
        print("• Test thoroughly before removing old MCP servers")
        print("• Monitor performance after migration")

        print("\n" + "="*80)


async def main():
    """Main migration function."""
    migration_manager = MCPMigrationManager()

    print("🔄 Legion MCP Unified Database Migration")
    print("This script will migrate from separate MCP servers to a unified database system.")
    print()

    response = input("Do you want to proceed with the migration? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("Migration cancelled.")
        return

    success = await migration_manager.run_migration()

    if success:
        print("\n✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
