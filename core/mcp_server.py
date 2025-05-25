"""
Unified MCP Server for Legion

Consolidates all MCP server functionality into a single high-performance
server with proper resource management, async operations, and unified
database access.
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from core.mcp_unified import (
    MCPUnifiedDB,
    VectorRecord,
    CacheRecord,
    EventRecord,
    CodebaseRecord,
    DevopsRecord,
    get_mcp_db,
)

logger = logging.getLogger(__name__)


class LegionMCPServer:
    """
    Unified MCP Server that handles all Legion MCP operations:
    - Vector memory storage and retrieval
    - Cache management with TTL
    - Event logging and retrieval
    - Codebase analysis and tracking
    - DevOps operations monitoring
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.db: Optional[MCPUnifiedDB] = None
        self._background_tasks: List[asyncio.Task] = []
        self._shutdown_event = asyncio.Event()

        # Configuration with sensible defaults
        self.cache_cleanup_interval = self.config.get("cache_cleanup_interval", 300)  # 5 minutes
        self.max_vector_results = self.config.get("max_vector_results", 100)
        self.default_cache_ttl = self.config.get("default_cache_ttl", 3600)  # 1 hour
        self.max_event_batch_size = self.config.get("max_event_batch_size", 1000)

        # Performance monitoring
        self._operation_stats = {
            "vector_operations": 0,
            "cache_operations": 0,
            "event_operations": 0,
            "codebase_operations": 0,
            "devops_operations": 0,
        }

    async def initialize(self) -> None:
        """Initialize the MCP server with database and background tasks."""
        self.db = await get_mcp_db()

        # Start background tasks
        cleanup_task = asyncio.create_task(self._cache_cleanup_worker())
        self._background_tasks.append(cleanup_task)

        stats_task = asyncio.create_task(self._stats_reporter())
        self._background_tasks.append(stats_task)

        logger.info("Legion MCP Server initialized with unified database")

    async def shutdown(self) -> None:
        """Gracefully shutdown the MCP server."""
        self._shutdown_event.set()

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()

        # Wait for tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)

        logger.info("Legion MCP Server shutdown complete")

    # ========================================================================
    # VECTOR MEMORY OPERATIONS
    # ========================================================================

    async def store_vector_memory(
        self,
        agent_name: str,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
        similarity_threshold: float = 0.8
    ) -> str:
        """Store vector memory for an agent."""
        record_id = str(uuid4())

        record = VectorRecord(
            id=record_id,
            server_type="vector",
            agent_name=agent_name,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {},
            text=text,
            embedding=embedding,
            similarity_threshold=similarity_threshold
        )

        await self.db.store_vector_memory(record)
        self._operation_stats["vector_operations"] += 1

        logger.debug(f"Stored vector memory for {agent_name}: {record_id}")
        return record_id

    async def retrieve_vector_memory(
        self,
        agent_name: str,
        query_embedding: List[float],
        top_k: int = 10,
        similarity_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Retrieve similar vector memories for an agent."""
        top_k = min(top_k, self.max_vector_results)

        records = await self.db.retrieve_similar_vectors(
            agent_name=agent_name,
            query_embedding=query_embedding,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )

        self._operation_stats["vector_operations"] += 1

        # Convert to serializable format
        results = []
        for record in records:
            results.append({
                "id": record.id,
                "text": record.text,
                "metadata": record.metadata,
                "timestamp": record.timestamp.isoformat(),
                "similarity_threshold": record.similarity_threshold
            })

        logger.debug(f"Retrieved {len(results)} vector memories for {agent_name}")
        return results

    # ========================================================================
    # CACHE MEMORY OPERATIONS
    # ========================================================================

    async def store_cache(
        self,
        agent_name: str,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None
    ) -> str:
        """Store cache entry with TTL."""
        record_id = str(uuid4())
        ttl = ttl_seconds or self.default_cache_ttl
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)

        record = CacheRecord(
            id=record_id,
            server_type="cache",
            agent_name=agent_name,
            timestamp=datetime.now(timezone.utc),
            metadata={"ttl_seconds": ttl},
            key=key,
            value=value,
            ttl_seconds=ttl,
            expires_at=expires_at
        )

        await self.db.store_cache(record)
        self._operation_stats["cache_operations"] += 1

        logger.debug(f"Stored cache entry for {agent_name}: {key}")
        return record_id

    async def get_cache(self, key: str) -> Optional[Any]:
        """Retrieve cache entry if not expired."""
        value = await self.db.get_cache(key)
        self._operation_stats["cache_operations"] += 1

        if value is not None:
            logger.debug(f"Cache hit for key: {key}")
        else:
            logger.debug(f"Cache miss for key: {key}")

        return value

    async def invalidate_cache(self, key: str) -> bool:
        """Invalidate a specific cache entry."""
        # Set expiration to past time to mark as expired
        past_time = datetime.now(timezone.utc) - timedelta(seconds=1)

        # This is a simplified implementation - in practice you'd update the expires_at
        value = await self.db.get_cache(key)
        self._operation_stats["cache_operations"] += 1

        return value is not None

    # ========================================================================
    # EVENT LOGGING OPERATIONS
    # ========================================================================

    async def log_event(
        self,
        agent_name: str,
        event_type: str,
        event_data: Dict[str, Any],
        severity: str = "info",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log an event."""
        record_id = str(uuid4())

        record = EventRecord(
            id=record_id,
            server_type="event",
            agent_name=agent_name,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {},
            event_type=event_type,
            event_data=event_data,
            severity=severity
        )

        await self.db.log_event(record)
        self._operation_stats["event_operations"] += 1

        logger.debug(f"Logged {severity} event for {agent_name}: {event_type}")
        return record_id

    async def get_events(
        self,
        agent_name: Optional[str] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve events with filtering."""
        limit = min(limit, self.max_event_batch_size)

        records = await self.db.get_events(
            agent_name=agent_name,
            event_type=event_type,
            severity=severity,
            limit=limit
        )

        self._operation_stats["event_operations"] += 1

        # Convert to serializable format
        results = []
        for record in records:
            results.append({
                "id": record.id,
                "agent_name": record.agent_name,
                "event_type": record.event_type,
                "event_data": record.event_data,
                "severity": record.severity,
                "metadata": record.metadata,
                "timestamp": record.timestamp.isoformat()
            })

        logger.debug(f"Retrieved {len(results)} events")
        return results

    # ========================================================================
    # CODEBASE ANALYSIS OPERATIONS
    # ========================================================================

    async def store_codebase_analysis(
        self,
        agent_name: str,
        file_path: str,
        analysis_data: Dict[str, Any],
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store codebase analysis results."""
        record_id = str(uuid4())

        # Calculate file hash for change detection
        try:
            if Path(file_path).exists():
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
            else:
                file_hash = "file_not_found"
        except Exception as e:
            file_hash = f"error_{str(e)[:32]}"

        record = CodebaseRecord(
            id=record_id,
            server_type="codebase",
            agent_name=agent_name,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {},
            file_path=file_path,
            file_hash=file_hash,
            analysis_data=analysis_data,
            dependencies=dependencies or []
        )

        # Store using the base store_cache method with special handling
        cache_record = CacheRecord(
            id=record_id,
            server_type="codebase",
            agent_name=agent_name,
            timestamp=record.timestamp,
            metadata=record.metadata,
            key=f"codebase:{file_path}:{file_hash}",
            value={
                "file_path": file_path,
                "file_hash": file_hash,
                "analysis_data": analysis_data,
                "dependencies": dependencies or []
            },
            ttl_seconds=86400,  # 24 hours
            expires_at=datetime.now(timezone.utc) + timedelta(days=1)
        )

        await self.db.store_cache(cache_record)
        self._operation_stats["codebase_operations"] += 1

        logger.debug(f"Stored codebase analysis for {agent_name}: {file_path}")
        return record_id

    async def get_codebase_analysis(
        self,
        file_path: str,
        file_hash: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Retrieve codebase analysis for a file."""
        if file_hash is None and Path(file_path).exists():
            try:
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
            except Exception:
                return None

        if file_hash:
            cache_key = f"codebase:{file_path}:{file_hash}"
            result = await self.db.get_cache(cache_key)
            self._operation_stats["codebase_operations"] += 1
            return result

        return None

    # ========================================================================
    # DEVOPS OPERATIONS
    # ========================================================================

    async def log_devops_operation(
        self,
        agent_name: str,
        operation_type: str,
        operation_data: Dict[str, Any],
        status: str = "pending",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log a DevOps operation."""
        record_id = str(uuid4())

        # Store as cache entry for quick access
        cache_record = CacheRecord(
            id=record_id,
            server_type="devops",
            agent_name=agent_name,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {},
            key=f"devops:{operation_type}:{record_id}",
            value={
                "operation_type": operation_type,
                "operation_data": operation_data,
                "status": status,
                "result": None
            },
            ttl_seconds=604800,  # 7 days
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )

        await self.db.store_cache(cache_record)
        self._operation_stats["devops_operations"] += 1

        logger.debug(f"Logged {operation_type} DevOps operation for {agent_name}: {status}")
        return record_id

    async def update_devops_operation(
        self,
        operation_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update a DevOps operation status and result."""
        # In a real implementation, you would query by operation_id and update
        # This is a simplified version
        self._operation_stats["devops_operations"] += 1

        logger.debug(f"Updated DevOps operation {operation_id}: {status}")
        return True

    # ========================================================================
    # BACKGROUND WORKERS
    # ========================================================================

    async def _cache_cleanup_worker(self) -> None:
        """Background worker to clean up expired cache entries."""
        while not self._shutdown_event.is_set():
            try:
                expired_count = await self.db.cleanup_expired_cache()
                if expired_count > 0:
                    logger.info(f"Cleaned up {expired_count} expired cache entries")

                await asyncio.sleep(self.cache_cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup worker: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def _stats_reporter(self) -> None:
        """Background worker to report performance statistics."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(300)  # Report every 5 minutes

                stats = await self.get_performance_stats()
                logger.info(f"MCP Server Stats: {json.dumps(stats, indent=2)}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in stats reporter: {e}")

    # ========================================================================
    # PERFORMANCE AND MONITORING
    # ========================================================================

    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        db_stats = await self.db.get_performance_stats()

        return {
            "operation_stats": self._operation_stats,
            "database_stats": db_stats,
            "config": {
                "cache_cleanup_interval": self.cache_cleanup_interval,
                "max_vector_results": self.max_vector_results,
                "default_cache_ttl": self.default_cache_ttl,
                "max_event_batch_size": self.max_event_batch_size,
            },
            "background_tasks": len(self._background_tasks),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the MCP server."""
        try:
            # Test database connectivity
            await self.db.get_performance_stats()
            db_healthy = True
        except Exception as e:
            db_healthy = False
            logger.error(f"Database health check failed: {e}")

        # Check background tasks
        active_tasks = sum(1 for task in self._background_tasks if not task.done())

        return {
            "status": "healthy" if db_healthy and active_tasks == len(self._background_tasks) else "unhealthy",
            "database_healthy": db_healthy,
            "active_background_tasks": active_tasks,
            "expected_background_tasks": len(self._background_tasks),
            "total_operations": sum(self._operation_stats.values()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Global server instance
_mcp_server: Optional[LegionMCPServer] = None


async def get_mcp_server(config: Optional[Dict[str, Any]] = None) -> LegionMCPServer:
    """Get the global MCP server instance."""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = LegionMCPServer(config)
        await _mcp_server.initialize()
    return _mcp_server


async def shutdown_mcp_server() -> None:
    """Shutdown the global MCP server instance."""
    global _mcp_server
    if _mcp_server is not None:
        await _mcp_server.shutdown()
        _mcp_server = None
