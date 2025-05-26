#!/usr/bin/env python3
"""
Performance monitoring script for Legion MCP Unified Database

This script provides real-time monitoring, performance analysis, and
optimization recommendations for the unified MCP database system.
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.mcp_server import get_mcp_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPPerformanceMonitor:
    """Real-time performance monitor for the unified MCP system."""

    def __init__(self, monitor_interval: int = 30):
        self.monitor_interval = monitor_interval
        self.start_time = time.time()
        self.baseline_stats = None
        self.performance_history = []
        self.alerts = []

    async def start_monitoring(self) -> None:
        """Start real-time performance monitoring."""
        logger.info("Starting MCP performance monitoring...")

        try:
            # Get initial baseline
            server = await get_mcp_server()
            self.baseline_stats = await server.get_performance_stats()

            print("🔍 Legion MCP Performance Monitor")
            print("="*60)
            print(f"Monitor interval: {self.monitor_interval} seconds")
            print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)

            # Start monitoring loop
            while True:
                await self._collect_metrics()
                await self._analyze_performance()
                await self._print_dashboard()
                await asyncio.sleep(self.monitor_interval)

        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            await self._print_final_report()
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")

    async def _collect_metrics(self) -> None:
        """Collect current performance metrics."""
        try:
            server = await get_mcp_server()

            # Get comprehensive stats
            stats = await server.get_performance_stats()
            health = await server.health_check()

            # Calculate uptime
            uptime = time.time() - self.start_time

            # Create performance snapshot
            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': uptime,
                'health': health,
                'stats': stats,
                'calculated_metrics': await self._calculate_derived_metrics(stats)
            }

            self.performance_history.append(snapshot)

            # Keep only last 100 snapshots to prevent memory issues
            if len(self.performance_history) > 100:
                self.performance_history = self.performance_history[-100:]

        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")

    async def _calculate_derived_metrics(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived performance metrics."""
        db_stats = stats.get('database_stats', {})
        op_stats = stats.get('operation_stats', {})

        # Calculate total operations
        total_ops = sum(op_stats.values())

        # Calculate operations per second if we have history
        ops_per_second = 0
        if len(self.performance_history) >= 2:
            prev_stats = self.performance_history[-2]['stats']['operation_stats']
            prev_total = sum(prev_stats.values())
            time_diff = self.monitor_interval
            ops_per_second = (total_ops - prev_total) / time_diff

        # Calculate database efficiency
        db_efficiency = 0
        if db_stats.get('total_queries', 0) > 0:
            avg_time = db_stats.get('avg_query_time', 0)
            db_efficiency = max(0, 100 - (avg_time * 100))  # Inverted - lower time = higher efficiency

        # Calculate memory usage estimate
        table_stats = db_stats.get('table_stats', {})
        total_records = sum(table_stats.values())

        return {
            'total_operations': total_ops,
            'operations_per_second': round(ops_per_second, 2),
            'database_efficiency_percent': round(db_efficiency, 2),
            'total_database_records': total_records,
            'slow_query_ratio': self._calculate_slow_query_ratio(db_stats),
            'cache_hit_estimation': self._estimate_cache_performance(op_stats)
        }

    def _calculate_slow_query_ratio(self, db_stats: Dict[str, Any]) -> float:
        """Calculate the ratio of slow queries."""
        total_queries = db_stats.get('total_queries', 0)
        slow_queries = db_stats.get('slow_queries', 0)

        if total_queries == 0:
            return 0.0

        return round((slow_queries / total_queries) * 100, 2)

    def _estimate_cache_performance(self, op_stats: Dict[str, Any]) -> float:
        """Estimate cache hit rate based on operation patterns."""
        cache_ops = op_stats.get('cache_operations', 0)
        total_ops = sum(op_stats.values())

        if total_ops == 0:
            return 0.0

        # This is a rough estimation - in production you'd track actual hits/misses
        cache_ratio = (cache_ops / total_ops) * 100
        return round(min(cache_ratio * 2, 100), 2)  # Rough estimation

    async def _analyze_performance(self) -> None:
        """Analyze performance and generate alerts."""
        if not self.performance_history:
            return

        current = self.performance_history[-1]
        metrics = current['calculated_metrics']
        db_stats = current['stats']['database_stats']

        # Clear old alerts
        self.alerts = []

        # Check for performance issues
        if metrics['operations_per_second'] > 100:
            self.alerts.append({
                'level': 'warning',
                'message': f"High operation rate: {metrics['operations_per_second']} ops/sec"
            })

        if metrics['slow_query_ratio'] > 10:
            self.alerts.append({
                'level': 'error',
                'message': f"High slow query ratio: {metrics['slow_query_ratio']}%"
            })

        if db_stats.get('avg_query_time', 0) > 2.0:
            self.alerts.append({
                'level': 'warning',
                'message': f"High average query time: {db_stats.get('avg_query_time', 0):.2f}s"
            })

        if current['health']['status'] != 'healthy':
            self.alerts.append({
                'level': 'critical',
                'message': f"System unhealthy: {current['health']}"
            })

        # Check connection pool utilization
        pool_size = db_stats.get('connection_pool_size', 0)
        if pool_size < 5:
            self.alerts.append({
                'level': 'info',
                'message': f"Low connection pool size: {pool_size}"
            })

    async def _print_dashboard(self) -> None:
        """Print real-time dashboard."""
        if not self.performance_history:
            return

        current = self.performance_history[-1]
        metrics = current['calculated_metrics']
        db_stats = current['stats']['database_stats']
        op_stats = current['stats']['operation_stats']

        # Clear screen (works on most terminals)
        print("\033[2J\033[H")

        print("🔍 Legion MCP Performance Dashboard")
        print("="*60)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
              f"Uptime: {self._format_uptime(current['uptime_seconds'])}")
        print("="*60)

        # System Health
        health_icon = "✅" if current['health']['status'] == 'healthy' else "❌"
        print(f"\n🏥 SYSTEM HEALTH {health_icon}")
        print(f"Status: {current['health']['status']}")
        print(f"Database: {'✅' if current['health']['database_healthy'] else '❌'}")
        print(f"Background Tasks: {current['health']['active_background_tasks']}/{current['health']['expected_background_tasks']}")

        # Performance Metrics
        print("\n📊 PERFORMANCE METRICS")
        print(f"Operations/sec: {metrics['operations_per_second']}")
        print(f"DB Efficiency: {metrics['database_efficiency_percent']}%")
        print(f"Avg Query Time: {db_stats.get('avg_query_time', 0):.3f}s")
        print(f"Slow Query Ratio: {metrics['slow_query_ratio']}%")
        print(f"Cache Hit Est.: {metrics['cache_hit_estimation']}%")

        # Database Statistics
        print("\n💾 DATABASE STATISTICS")
        print(f"Total Records: {metrics['total_database_records']:,}")
        print(f"Total Queries: {db_stats.get('total_queries', 0):,}")
        print(f"Connection Pool: {db_stats.get('connection_pool_size', 0)}")

        # Operation Breakdown
        print("\n🔧 OPERATION BREAKDOWN")
        for op_type, count in op_stats.items():
            percentage = (count / max(sum(op_stats.values()), 1)) * 100
            print(f"{op_type.replace('_', ' ').title()}: {count:,} ({percentage:.1f}%)")

        # Table Statistics
        table_stats = db_stats.get('table_stats', {})
        if table_stats:
            print("\n📋 TABLE STATISTICS")
            for table, count in table_stats.items():
                print(f"{table.replace('_', ' ').title()}: {count:,} records")

        # Alerts
        if self.alerts:
            print("\n🚨 ALERTS")
            for alert in self.alerts:
                icon = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "critical": "🔥"}.get(alert['level'], "❓")
                print(f"{icon} {alert['message']}")
        else:
            print("\n✅ NO ALERTS")

        # Performance Recommendations
        recommendations = self._get_performance_recommendations(metrics, db_stats)
        if recommendations:
            print("\n💡 RECOMMENDATIONS")
            for rec in recommendations:
                print(f"• {rec}")

        print(f"\n{'='*60}")
        print("Press Ctrl+C to stop monitoring")

    def _get_performance_recommendations(self, metrics: Dict[str, Any], db_stats: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []

        if metrics['slow_query_ratio'] > 5:
            recommendations.append("Consider optimizing slow queries or adding indexes")

        if db_stats.get('connection_pool_size', 0) < 10 and metrics['operations_per_second'] > 50:
            recommendations.append("Consider increasing connection pool size")

        if metrics['total_database_records'] > 100000:
            recommendations.append("Consider implementing data archival for old records")

        if db_stats.get('avg_query_time', 0) > 1.0:
            recommendations.append("Database queries are slow - check indexes and query optimization")

        if metrics['cache_hit_estimation'] < 70:
            recommendations.append("Consider increasing cache TTL or cache size")

        return recommendations

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format."""
        seconds = int(seconds)
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        else:
            return f"{minutes}m {secs}s"

    async def _print_final_report(self) -> None:
        """Print final performance report."""
        if not self.performance_history:
            return

        print("\n" + "="*60)
        print("📊 FINAL PERFORMANCE REPORT")
        print("="*60)

        # Calculate summary statistics
        total_uptime = time.time() - self.start_time

        # Get min/max/avg metrics
        if len(self.performance_history) > 1:
            ops_per_sec = [h['calculated_metrics']['operations_per_second'] for h in self.performance_history[1:]]
            query_times = [h['stats']['database_stats'].get('avg_query_time', 0) for h in self.performance_history]

            print("\n⏱️  UPTIME SUMMARY")
            print(f"Total Uptime: {self._format_uptime(total_uptime)}")
            print(f"Monitoring Sessions: {len(self.performance_history)}")

            if ops_per_sec:
                print("\n🚀 OPERATIONS SUMMARY")
                print(f"Avg Ops/sec: {sum(ops_per_sec) / len(ops_per_sec):.2f}")
                print(f"Max Ops/sec: {max(ops_per_sec):.2f}")
                print(f"Min Ops/sec: {min(ops_per_sec):.2f}")

            if query_times:
                print("\n⚡ QUERY PERFORMANCE")
                print(f"Avg Query Time: {sum(query_times) / len(query_times):.3f}s")
                print(f"Max Query Time: {max(query_times):.3f}s")
                print(f"Min Query Time: {min(query_times):.3f}s")

            # Final recommendations
            final_metrics = self.performance_history[-1]['calculated_metrics']
            final_db_stats = self.performance_history[-1]['stats']['database_stats']
            recommendations = self._get_performance_recommendations(final_metrics, final_db_stats)

            if recommendations:
                print("\n💡 FINAL RECOMMENDATIONS")
                for rec in recommendations:
                    print(f"• {rec}")

            print("\n✅ Monitoring completed successfully!")

        print("="*60)


async def main():
    """Main monitoring function."""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor Legion MCP performance")
    parser.add_argument("--interval", type=int, default=30, help="Monitor interval in seconds")
    parser.add_argument("--duration", type=int, help="Monitor duration in seconds (default: infinite)")
    parser.add_argument("--export", help="Export report to file")

    args = parser.parse_args()

    monitor = MCPPerformanceMonitor(monitor_interval=args.interval)

    if args.duration:
        print(f"Monitoring for {args.duration} seconds...")
        # Run for specific duration
        task = asyncio.create_task(monitor.start_monitoring())
        try:
            await asyncio.wait_for(task, timeout=args.duration)
        except asyncio.TimeoutError:
            task.cancel()
            print(f"\n⏰ Monitoring completed after {args.duration} seconds")
    else:
        # Run indefinitely
        await monitor.start_monitoring()

    # Export report if requested
    if args.export and monitor.performance_history:
        with open(args.export, 'w') as f:
            json.dump(monitor.performance_history, f, indent=2)
        print(f"📄 Performance data exported to {args.export}")


if __name__ == "__main__":
    asyncio.run(main())
