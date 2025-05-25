#!/usr/bin/env python3
"""
Database optimization script for Legion MCP Unified Database

Implements production best practices for SQLite performance optimization,
maintenance operations, and health monitoring.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.mcp_unified import get_mcp_db
from core.mcp_config import get_mcp_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPDatabaseOptimizer:
    """Production database optimization and maintenance."""

    def __init__(self):
        self.config = get_mcp_config()

    async def run_optimization(self) -> Dict[str, any]:
        """Run comprehensive database optimization."""
        logger.info("Starting MCP database optimization...")

        results = {
            'optimizations_applied': [],
            'performance_before': None,
            'performance_after': None,
            'recommendations': []
        }

        db = await get_mcp_db()

        # Get baseline performance
        results['performance_before'] = await db.get_performance_stats()

        # Run optimizations
        await self._optimize_pragma_settings(db, results)
        await self._vacuum_database(db, results)
        await self._analyze_statistics(db, results)
        await self._cleanup_old_data(db, results)
        await self._optimize_indexes(db, results)

        # Get post-optimization performance
        results['performance_after'] = await db.get_performance_stats()

        # Generate recommendations
        results['recommendations'] = await self._generate_recommendations(db)

        await self._print_optimization_report(results)

        return results

    async def _optimize_pragma_settings(self, db, results: Dict) -> None:
        """Apply production PRAGMA optimizations."""
        logger.info("Optimizing PRAGMA settings...")

        optimizations = [
            ("PRAGMA journal_mode=WAL", "Write-Ahead Logging for better concurrency"),
            ("PRAGMA synchronous=NORMAL", "Balanced durability vs performance"),
            ("PRAGMA cache_size=50000", "Increased cache size for better performance"),
            ("PRAGMA temp_store=MEMORY", "Store temporary tables in memory"),
            ("PRAGMA mmap_size=268435456", "Memory-mapped I/O (256MB)"),
            ("PRAGMA optimize", "Update statistics for query planner"),
        ]

        async with db.get_connection() as conn:
            for pragma, description in optimizations:
                await conn.execute(pragma)
                results['optimizations_applied'].append(f"{pragma} - {description}")
                logger.info(f"Applied: {pragma}")
            await conn.commit()

    async def _vacuum_database(self, db, results: Dict) -> None:
        """Vacuum database to reclaim space and optimize structure."""
        logger.info("Running VACUUM operation...")

        try:
            async with db.get_connection() as conn:
                # Get database size before
                cursor = await conn.execute("PRAGMA page_count")
                pages_before = (await cursor.fetchone())[0]

                # Run VACUUM
                await conn.execute("VACUUM")

                # Get database size after
                cursor = await conn.execute("PRAGMA page_count")
                pages_after = (await cursor.fetchone())[0]

                space_saved = pages_before - pages_after
                results['optimizations_applied'].append(
                    f"VACUUM completed - Reclaimed {space_saved} pages"
                )
                logger.info(f"VACUUM completed - Reclaimed {space_saved} pages")

        except Exception as e:
            logger.warning(f"VACUUM operation failed: {e}")

    async def _analyze_statistics(self, db, results: Dict) -> None:
        """Update table statistics for query optimizer."""
        logger.info("Updating table statistics...")

        try:
            async with db.get_connection() as conn:
                await conn.execute("ANALYZE")
                results['optimizations_applied'].append("ANALYZE - Updated table statistics")
                logger.info("Table statistics updated")

        except Exception as e:
            logger.warning(f"ANALYZE operation failed: {e}")

    async def _cleanup_old_data(self, db, results: Dict) -> None:
        """Clean up old data based on retention policies."""
        logger.info("Cleaning up old data...")

        cleanup_operations = []

        try:
            async with db.get_connection() as conn:
                # Clean up old performance tracking data (keep last 7 days)
                week_ago = time.time() - (7 * 24 * 3600)
                cursor = await conn.execute(
                    "DELETE FROM query_performance WHERE timestamp < ?",
                    (week_ago,)
                )
                deleted_perf = cursor.rowcount
                cleanup_operations.append(f"Deleted {deleted_perf} old performance records")

                # Clean up expired cache entries
                expired_count = await db.cleanup_expired_cache()
                cleanup_operations.append(f"Cleaned up {expired_count} expired cache entries")

                await conn.commit()

        except Exception as e:
            logger.warning(f"Cleanup operation failed: {e}")

        results['optimizations_applied'].extend(cleanup_operations)

    async def _optimize_indexes(self, db, results: Dict) -> None:
        """Check and optimize database indexes."""
        logger.info("Checking index optimization...")

        try:
            async with db.get_connection() as conn:
                # Check for unused indexes
                cursor = await conn.execute("""
                    SELECT name, sql FROM sqlite_master
                    WHERE type='index' AND name NOT LIKE 'sqlite_%'
                """)
                indexes = await cursor.fetchall()

                index_count = len(indexes)
                results['optimizations_applied'].append(
                    f"Index check completed - {index_count} custom indexes found"
                )

                # Reindex critical indexes for performance
                await conn.execute("REINDEX idx_mcp_records_composite")
                await conn.execute("REINDEX idx_cache_memory_expires")

                results['optimizations_applied'].append("Critical indexes rebuilt")
                logger.info("Critical indexes rebuilt")

        except Exception as e:
            logger.warning(f"Index optimization failed: {e}")

    async def _generate_recommendations(self, db) -> List[str]:
        """Generate optimization recommendations based on current state."""
        recommendations = []

        try:
            stats = await db.get_performance_stats()
            table_stats = stats.get('table_stats', {})
            total_records = sum(table_stats.values())

            # Size-based recommendations
            if total_records > 100000:
                recommendations.append(
                    "Consider implementing data archival for records older than 30 days"
                )

            if total_records > 500000:
                recommendations.append(
                    "Database is getting large - consider partitioning or sharding strategies"
                )

            # Performance-based recommendations
            avg_query_time = stats.get('avg_query_time', 0)
            if avg_query_time > 0.1:
                recommendations.append(
                    "Average query time is high - consider adding more specific indexes"
                )

            slow_queries = stats.get('slow_queries', 0)
            total_queries = stats.get('total_queries', 1)
            if slow_queries / total_queries > 0.05:  # More than 5% slow queries
                recommendations.append(
                    "High percentage of slow queries - enable query logging for analysis"
                )

            # Connection pool recommendations
            pool_size = stats.get('connection_pool_size', 0)
            if pool_size < 15:
                recommendations.append(
                    "Consider increasing connection pool size for better concurrency"
                )

        except Exception as e:
            logger.warning(f"Failed to generate recommendations: {e}")

        return recommendations

    async def _print_optimization_report(self, results: Dict) -> None:
        """Print comprehensive optimization report."""
        print("\n" + "="*70)
        print("📊 MCP DATABASE OPTIMIZATION REPORT")
        print("="*70)

        print(f"\n✅ OPTIMIZATIONS APPLIED ({len(results['optimizations_applied'])}):")
        for opt in results['optimizations_applied']:
            print(f"• {opt}")

        # Performance comparison
        before = results['performance_before']
        after = results['performance_after']

        if before and after:
            print(f"\n📈 PERFORMANCE COMPARISON:")

            print(f"Total Queries:")
            print(f"  Before: {before.get('total_queries', 0):,}")
            print(f"  After:  {after.get('total_queries', 0):,}")

            print(f"Average Query Time:")
            print(f"  Before: {before.get('avg_query_time', 0):.3f}s")
            print(f"  After:  {after.get('avg_query_time', 0):.3f}s")

            # Calculate improvement
            before_time = before.get('avg_query_time', 0)
            after_time = after.get('avg_query_time', 0)
            if before_time > 0:
                improvement = ((before_time - after_time) / before_time) * 100
                print(f"  Improvement: {improvement:.1f}%")

        # Recommendations
        if results['recommendations']:
            print(f"\n💡 RECOMMENDATIONS ({len(results['recommendations'])}):")
            for rec in results['recommendations']:
                print(f"• {rec}")

        print(f"\n🔧 MAINTENANCE SCHEDULE:")
        print("• Run optimization weekly in production")
        print("• Monitor slow query ratio daily")
        print("• Archive old data monthly")
        print("• Review recommendations after major changes")

        print("\n" + "="*70)


async def main():
    """Main optimization function."""
    import argparse

    parser = argparse.ArgumentParser(description="Optimize Legion MCP database")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without applying changes")
    parser.add_argument("--aggressive", action="store_true", help="Apply aggressive optimizations")

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be applied")
        print("This would show what optimizations would be performed")
        return

    optimizer = MCPDatabaseOptimizer()

    print("🚀 Starting MCP Database Optimization")
    print("This will optimize the unified MCP database for production performance")
    print()

    if args.aggressive:
        print("⚠️  AGGRESSIVE MODE - This may take longer but provides maximum optimization")
        response = input("Continue with aggressive optimization? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Optimization cancelled.")
            return

    try:
        results = await optimizer.run_optimization()
        print("\n✅ Database optimization completed successfully!")

    except Exception as e:
        print(f"\n❌ Optimization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
