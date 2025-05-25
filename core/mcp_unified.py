"""
Unified MCP Database System for Legion

Consolidates vector memory, cache memory, event logging, codebase analysis,
and devops operations into a single high-performance database with proper
indexing, connection pooling, and async operations.
"""

import asyncio
import json
import logging
import sqlite3
import threading
import time
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from uuid import uuid4

import aiosqlite

logger = logging.getLogger(__name__)


@dataclass
class MCPRecord:
    """Base record for all MCP operations."""
    id: str
    server_type: str  # vector, cache, event, codebase, devops
    agent_name: str
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class VectorRecord(MCPRecord):
    """Vector memory record with embeddings."""
    text: str
    embedding: List[float]
    similarity_threshold: float = 0.8


@dataclass
class CacheRecord(MCPRecord):
    """Cache memory record with TTL."""
    key: str
    value: Any
    ttl_seconds: int
    expires_at: datetime


@dataclass
class EventRecord(MCPRecord):
    """Event log record with structured data."""
    event_type: str
    event_data: Dict[str, Any]
    severity: str  # debug, info, warning, error, critical


@dataclass
class CodebaseRecord(MCPRecord):
    """Codebase analysis record."""
    file_path: str
    file_hash: str
    analysis_data: Dict[str, Any]
    dependencies: List[str]


@dataclass
class DevopsRecord(MCPRecord):
    """DevOps operation record."""
    operation_type: str  # deploy, rollback, scale, monitor
    operation_data: Dict[str, Any]
    status: str  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None


class MCPUnifiedDB:
    """
    Unified MCP Database with connection pooling, async operations,
    and optimized indexes for all MCP server types.
    """

    def __init__(self, db_path: str = "memory/db/mcp_unified.db", pool_size: int = 10):
        self.db_path = Path(db_path)
        self.pool_size = pool_size
        self._connection_pool: List[aiosqlite.Connection] = []
        self._pool_lock = asyncio.Lock()
        self._initialized = False

        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Performance monitoring
        self._query_stats = {
            "total_queries": 0,
            "avg_query_time": 0.0,
            "slow_queries": 0
        }

    async def initialize(self) -> None:
        """Initialize database schema and connection pool."""
        if self._initialized:
            return

        # Create initial connection for schema setup
        async with aiosqlite.connect(self.db_path) as conn:
            await self._create_schema(conn)
            await self._create_indexes(conn)

        # Initialize connection pool
        for _ in range(self.pool_size):
            conn = await aiosqlite.connect(self.db_path)
            conn.row_factory = aiosqlite.Row
            await conn.execute("PRAGMA journal_mode=WAL")
            await conn.execute("PRAGMA synchronous=NORMAL")
            await conn.execute("PRAGMA cache_size=10000")
            await conn.execute("PRAGMA temp_store=MEMORY")
            self._connection_pool.append(conn)

        self._initialized = True
        logger.info(f"Initialized MCP Unified DB with {self.pool_size} connections")

    async def _create_schema(self, conn: aiosqlite.Connection) -> None:
        """Create unified schema for all MCP server types."""
        schema_sql = """
        -- Unified records table
        CREATE TABLE IF NOT EXISTS mcp_records (
            id TEXT PRIMARY KEY,
            server_type TEXT NOT NULL,
            agent_name TEXT NOT NULL,
            timestamp REAL NOT NULL,
            metadata TEXT NOT NULL
        );

        -- Vector memory table
        CREATE TABLE IF NOT EXISTS vector_memory (
            record_id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            embedding BLOB NOT NULL,
            similarity_threshold REAL DEFAULT 0.8,
            FOREIGN KEY (record_id) REFERENCES mcp_records(id)
        );

        -- Cache memory table
        CREATE TABLE IF NOT EXISTS cache_memory (
            record_id TEXT PRIMARY KEY,
            cache_key TEXT NOT NULL,
            cache_value TEXT NOT NULL,
            ttl_seconds INTEGER NOT NULL,
            expires_at REAL NOT NULL,
            FOREIGN KEY (record_id) REFERENCES mcp_records(id)
        );

        -- Event log table
        CREATE TABLE IF NOT EXISTS event_log (
            record_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            event_data TEXT NOT NULL,
            severity TEXT NOT NULL,
            FOREIGN KEY (record_id) REFERENCES mcp_records(id)
        );

        -- Codebase analysis table
        CREATE TABLE IF NOT EXISTS codebase_analysis (
            record_id TEXT PRIMARY KEY,
            file_path TEXT NOT NULL,
            file_hash TEXT NOT NULL,
            analysis_data TEXT NOT NULL,
            dependencies TEXT NOT NULL,
            FOREIGN KEY (record_id) REFERENCES mcp_records(id)
        );

        -- DevOps operations table
        CREATE TABLE IF NOT EXISTS devops_operations (
            record_id TEXT PRIMARY KEY,
            operation_type TEXT NOT NULL,
            operation_data TEXT NOT NULL,
            status TEXT NOT NULL,
            result TEXT,
            FOREIGN KEY (record_id) REFERENCES mcp_records(id)
        );

        -- Query performance tracking
        CREATE TABLE IF NOT EXISTS query_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_type TEXT NOT NULL,
            execution_time REAL NOT NULL,
            timestamp REAL NOT NULL
        );
        """

        await conn.executescript(schema_sql)
        await conn.commit()

    async def _create_indexes(self, conn: aiosqlite.Connection) -> None:
        """Create optimized indexes for query performance."""
        indexes_sql = """
        -- Core indexes
        CREATE INDEX IF NOT EXISTS idx_mcp_records_server_type ON mcp_records(server_type);
        CREATE INDEX IF NOT EXISTS idx_mcp_records_agent_name ON mcp_records(agent_name);
        CREATE INDEX IF NOT EXISTS idx_mcp_records_timestamp ON mcp_records(timestamp);
        CREATE INDEX IF NOT EXISTS idx_mcp_records_composite ON mcp_records(server_type, agent_name, timestamp);

        -- Vector memory indexes
        CREATE INDEX IF NOT EXISTS idx_vector_memory_threshold ON vector_memory(similarity_threshold);

        -- Cache memory indexes
        CREATE INDEX IF NOT EXISTS idx_cache_memory_key ON cache_memory(cache_key);
        CREATE INDEX IF NOT EXISTS idx_cache_memory_expires ON cache_memory(expires_at);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_cache_memory_unique_key ON cache_memory(cache_key);

        -- Event log indexes
        CREATE INDEX IF NOT EXISTS idx_event_log_type ON event_log(event_type);
        CREATE INDEX IF NOT EXISTS idx_event_log_severity ON event_log(severity);
        CREATE INDEX IF NOT EXISTS idx_event_log_composite ON event_log(event_type, severity);

        -- Codebase analysis indexes
        CREATE INDEX IF NOT EXISTS idx_codebase_file_path ON codebase_analysis(file_path);
        CREATE INDEX IF NOT EXISTS idx_codebase_file_hash ON codebase_analysis(file_hash);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_codebase_unique_file ON codebase_analysis(file_path, file_hash);

        -- DevOps operations indexes
        CREATE INDEX IF NOT EXISTS idx_devops_operation_type ON devops_operations(operation_type);
        CREATE INDEX IF NOT EXISTS idx_devops_status ON devops_operations(status);
        CREATE INDEX IF NOT EXISTS idx_devops_composite ON devops_operations(operation_type, status);

        -- Performance indexes
        CREATE INDEX IF NOT EXISTS idx_query_performance_type ON query_performance(query_type);
        CREATE INDEX IF NOT EXISTS idx_query_performance_time ON query_performance(execution_time);
        """

        await conn.executescript(indexes_sql)
        await conn.commit()

    @asynccontextmanager
    async def get_connection(self):
        """Get connection from pool with automatic return."""
        async with self._pool_lock:
            if not self._connection_pool:
                raise RuntimeError("Connection pool exhausted")
            conn = self._connection_pool.pop()

        try:
            yield conn
        finally:
            async with self._pool_lock:
                self._connection_pool.append(conn)

    async def _track_query_performance(self, query_type: str, execution_time: float) -> None:
        """Track query performance for optimization."""
        self._query_stats["total_queries"] += 1
        self._query_stats["avg_query_time"] = (
            (self._query_stats["avg_query_time"] * (self._query_stats["total_queries"] - 1) + execution_time)
            / self._query_stats["total_queries"]
        )

        if execution_time > 1.0:  # Slow query threshold
            self._query_stats["slow_queries"] += 1
            logger.warning(f"Slow query detected: {query_type} took {execution_time:.2f}s")

        async with self.get_connection() as conn:
            await conn.execute(
                "INSERT INTO query_performance (query_type, execution_time, timestamp) VALUES (?, ?, ?)",
                (query_type, execution_time, time.time())
            )
            await conn.commit()

    async def store_vector_memory(self, record: VectorRecord) -> None:
        """Store vector memory with optimized embedding storage."""
        start_time = time.time()

        async with self.get_connection() as conn:
            # Store base record
            await conn.execute(
                "INSERT OR REPLACE INTO mcp_records (id, server_type, agent_name, timestamp, metadata) VALUES (?, ?, ?, ?, ?)",
                (record.id, record.server_type, record.agent_name, record.timestamp.timestamp(), json.dumps(record.metadata))
            )

            # Store vector data with binary embedding
            embedding_blob = json.dumps(record.embedding).encode('utf-8')
            await conn.execute(
                "INSERT OR REPLACE INTO vector_memory (record_id, text, embedding, similarity_threshold) VALUES (?, ?, ?, ?)",
                (record.id, record.text, embedding_blob, record.similarity_threshold)
            )

            await conn.commit()

        execution_time = time.time() - start_time
        await self._track_query_performance("store_vector_memory", execution_time)

    async def retrieve_similar_vectors(
        self,
        agent_name: str,
        query_embedding: List[float],
        top_k: int = 10,
        similarity_threshold: float = 0.8
    ) -> List[VectorRecord]:
        """Retrieve similar vectors using optimized similarity search."""
        start_time = time.time()

        async with self.get_connection() as conn:
            cursor = await conn.execute("""
                SELECT r.id, r.agent_name, r.timestamp, r.metadata,
                       v.text, v.embedding, v.similarity_threshold
                FROM mcp_records r
                JOIN vector_memory v ON r.id = v.record_id
                WHERE r.server_type = 'vector'
                AND r.agent_name = ?
                AND v.similarity_threshold >= ?
                ORDER BY r.timestamp DESC
                LIMIT ?
            """, (agent_name, similarity_threshold, top_k * 2))  # Get extra for similarity filtering

            rows = await cursor.fetchall()

            # Calculate similarities and filter
            results = []
            for row in rows:
                stored_embedding = json.loads(row['embedding'].decode('utf-8'))
                similarity = self._cosine_similarity(query_embedding, stored_embedding)

                if similarity >= similarity_threshold:
                    record = VectorRecord(
                        id=row['id'],
                        server_type='vector',
                        agent_name=row['agent_name'],
                        timestamp=datetime.fromtimestamp(row['timestamp'], tz=timezone.utc),
                        metadata=json.loads(row['metadata']),
                        text=row['text'],
                        embedding=stored_embedding,
                        similarity_threshold=row['similarity_threshold']
                    )
                    results.append((similarity, record))

            # Sort by similarity and return top_k
            results.sort(reverse=True, key=lambda x: x[0])

        execution_time = time.time() - start_time
        await self._track_query_performance("retrieve_similar_vectors", execution_time)

        return [record for _, record in results[:top_k]]

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    async def store_cache(self, record: CacheRecord) -> None:
        """Store cache entry with TTL."""
        start_time = time.time()

        async with self.get_connection() as conn:
            await conn.execute(
                "INSERT OR REPLACE INTO mcp_records (id, server_type, agent_name, timestamp, metadata) VALUES (?, ?, ?, ?, ?)",
                (record.id, record.server_type, record.agent_name, record.timestamp.timestamp(), json.dumps(record.metadata))
            )

            await conn.execute(
                "INSERT OR REPLACE INTO cache_memory (record_id, cache_key, cache_value, ttl_seconds, expires_at) VALUES (?, ?, ?, ?, ?)",
                (record.id, record.key, json.dumps(record.value), record.ttl_seconds, record.expires_at.timestamp())
            )

            await conn.commit()

        execution_time = time.time() - start_time
        await self._track_query_performance("store_cache", execution_time)

    async def get_cache(self, key: str) -> Optional[Any]:
        """Retrieve cache entry if not expired."""
        start_time = time.time()

        async with self.get_connection() as conn:
            cursor = await conn.execute("""
                SELECT cache_value, expires_at
                FROM cache_memory
                WHERE cache_key = ? AND expires_at > ?
            """, (key, time.time()))

            row = await cursor.fetchone()

        execution_time = time.time() - start_time
        await self._track_query_performance("get_cache", execution_time)

        if row:
            return json.loads(row['cache_value'])
        return None

    async def cleanup_expired_cache(self) -> int:
        """Remove expired cache entries."""
        start_time = time.time()

        async with self.get_connection() as conn:
            # Get expired record IDs
            cursor = await conn.execute(
                "SELECT record_id FROM cache_memory WHERE expires_at <= ?",
                (time.time(),)
            )
            expired_ids = [row['record_id'] for row in await cursor.fetchall()]

            if expired_ids:
                placeholders = ','.join('?' * len(expired_ids))
                await conn.execute(f"DELETE FROM cache_memory WHERE record_id IN ({placeholders})", expired_ids)
                await conn.execute(f"DELETE FROM mcp_records WHERE id IN ({placeholders})", expired_ids)
                await conn.commit()

        execution_time = time.time() - start_time
        await self._track_query_performance("cleanup_expired_cache", execution_time)

        return len(expired_ids)

    async def log_event(self, record: EventRecord) -> None:
        """Log structured event."""
        start_time = time.time()

        async with self.get_connection() as conn:
            await conn.execute(
                "INSERT INTO mcp_records (id, server_type, agent_name, timestamp, metadata) VALUES (?, ?, ?, ?, ?)",
                (record.id, record.server_type, record.agent_name, record.timestamp.timestamp(), json.dumps(record.metadata))
            )

            await conn.execute(
                "INSERT INTO event_log (record_id, event_type, event_data, severity) VALUES (?, ?, ?, ?)",
                (record.id, record.event_type, json.dumps(record.event_data), record.severity)
            )

            await conn.commit()

        execution_time = time.time() - start_time
        await self._track_query_performance("log_event", execution_time)

    async def get_events(
        self,
        agent_name: Optional[str] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[EventRecord]:
        """Retrieve events with filtering."""
        start_time = time.time()

        conditions = ["r.server_type = 'event'"]
        params = []

        if agent_name:
            conditions.append("r.agent_name = ?")
            params.append(agent_name)
        if event_type:
            conditions.append("e.event_type = ?")
            params.append(event_type)
        if severity:
            conditions.append("e.severity = ?")
            params.append(severity)

        params.append(limit)

        query = f"""
            SELECT r.id, r.agent_name, r.timestamp, r.metadata,
                   e.event_type, e.event_data, e.severity
            FROM mcp_records r
            JOIN event_log e ON r.id = e.record_id
            WHERE {' AND '.join(conditions)}
            ORDER BY r.timestamp DESC
            LIMIT ?
        """

        async with self.get_connection() as conn:
            cursor = await conn.execute(query, params)
            rows = await cursor.fetchall()

            results = []
            for row in rows:
                record = EventRecord(
                    id=row['id'],
                    server_type='event',
                    agent_name=row['agent_name'],
                    timestamp=datetime.fromtimestamp(row['timestamp'], tz=timezone.utc),
                    metadata=json.loads(row['metadata']),
                    event_type=row['event_type'],
                    event_data=json.loads(row['event_data']),
                    severity=row['severity']
                )
                results.append(record)

        execution_time = time.time() - start_time
        await self._track_query_performance("get_events", execution_time)

        return results

    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get database performance statistics."""
        async with self.get_connection() as conn:
            # Query performance stats
            cursor = await conn.execute("""
                SELECT query_type,
                       COUNT(*) as count,
                       AVG(execution_time) as avg_time,
                       MAX(execution_time) as max_time
                FROM query_performance
                WHERE timestamp > ?
                GROUP BY query_type
                ORDER BY avg_time DESC
            """, (time.time() - 3600,))  # Last hour

            query_stats = {row['query_type']: {
                'count': row['count'],
                'avg_time': row['avg_time'],
                'max_time': row['max_time']
            } for row in await cursor.fetchall()}

            # Table sizes
            table_stats = {}
            for table in ['mcp_records', 'vector_memory', 'cache_memory', 'event_log', 'codebase_analysis', 'devops_operations']:
                cursor = await conn.execute(f"SELECT COUNT(*) as count FROM {table}")
                row = await cursor.fetchone()
                table_stats[table] = row['count']

        return {
            'connection_pool_size': len(self._connection_pool),
            'total_queries': self._query_stats['total_queries'],
            'avg_query_time': self._query_stats['avg_query_time'],
            'slow_queries': self._query_stats['slow_queries'],
            'query_stats': query_stats,
            'table_stats': table_stats
        }

    async def close(self) -> None:
        """Close all connections in the pool."""
        async with self._pool_lock:
            for conn in self._connection_pool:
                await conn.close()
            self._connection_pool.clear()
        self._initialized = False


# Global instance
_mcp_db: Optional[MCPUnifiedDB] = None


async def get_mcp_db() -> MCPUnifiedDB:
    """Get the global MCP database instance."""
    global _mcp_db
    if _mcp_db is None:
        _mcp_db = MCPUnifiedDB()
        await _mcp_db.initialize()
    return _mcp_db


async def close_mcp_db() -> None:
    """Close the global MCP database instance."""
    global _mcp_db
    if _mcp_db is not None:
        await _mcp_db.close()
        _mcp_db = None
