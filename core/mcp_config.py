"""
Unified MCP Configuration for Legion

Provides centralized configuration management for the unified MCP server,
replacing the need for multiple separate MCP servers with a single
optimized instance.
"""

import json
import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for the unified MCP server."""

    # Database configuration
    db_path: str = "memory/db/mcp_unified.db"
    connection_pool_size: int = 10

    # Cache configuration
    default_cache_ttl: int = 3600  # 1 hour
    cache_cleanup_interval: int = 300  # 5 minutes
    max_cache_size: int = 10000  # entries

    # Vector memory configuration
    max_vector_results: int = 100
    default_similarity_threshold: float = 0.8
    vector_embedding_dimension: int = 1536  # OpenAI default

    # Event logging configuration
    max_event_batch_size: int = 1000
    event_retention_days: int = 30

    # Codebase analysis configuration
    codebase_cache_ttl: int = 86400  # 24 hours
    max_file_size_mb: int = 10

    # DevOps operations configuration
    devops_operation_ttl: int = 604800  # 7 days
    max_operation_history: int = 1000

    # Performance configuration
    query_timeout_seconds: int = 30
    slow_query_threshold: float = 1.0

    # Monitoring configuration
    stats_report_interval: int = 300  # 5 minutes
    health_check_interval: int = 60  # 1 minute

    # Security configuration
    enable_auth: bool = False
    auth_token: Optional[str] = None
    allowed_agents: Optional[List[str]] = None


class MCPConfigManager:
    """Manages MCP server configuration with environment variable support."""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "mcp_config.json"
        self._config: Optional[MCPServerConfig] = None

    def load_config(self) -> MCPServerConfig:
        """Load configuration from file and environment variables."""
        if self._config is not None:
            return self._config

        # Start with defaults
        config_data = {}

        # Load from file if it exists
        if Path(self.config_file).exists():
            try:
                with open(self.config_file) as f:
                    config_data = json.load(f)
                logger.info(f"Loaded MCP config from {self.config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file {self.config_file}: {e}")

        # Override with environment variables
        env_overrides = self._load_from_environment()
        config_data.update(env_overrides)

        # Create config object
        self._config = MCPServerConfig(**config_data)

        # Validate configuration
        self._validate_config(self._config)

        return self._config

    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        env_mapping = {
            # Database configuration
            "MCP_DB_PATH": "db_path",
            "MCP_CONNECTION_POOL_SIZE": ("connection_pool_size", int),

            # Cache configuration
            "MCP_DEFAULT_CACHE_TTL": ("default_cache_ttl", int),
            "MCP_CACHE_CLEANUP_INTERVAL": ("cache_cleanup_interval", int),
            "MCP_MAX_CACHE_SIZE": ("max_cache_size", int),

            # Vector memory configuration
            "MCP_MAX_VECTOR_RESULTS": ("max_vector_results", int),
            "MCP_DEFAULT_SIMILARITY_THRESHOLD": ("default_similarity_threshold", float),
            "MCP_VECTOR_EMBEDDING_DIMENSION": ("vector_embedding_dimension", int),

            # Event logging configuration
            "MCP_MAX_EVENT_BATCH_SIZE": ("max_event_batch_size", int),
            "MCP_EVENT_RETENTION_DAYS": ("event_retention_days", int),

            # Codebase analysis configuration
            "MCP_CODEBASE_CACHE_TTL": ("codebase_cache_ttl", int),
            "MCP_MAX_FILE_SIZE_MB": ("max_file_size_mb", int),

            # DevOps operations configuration
            "MCP_DEVOPS_OPERATION_TTL": ("devops_operation_ttl", int),
            "MCP_MAX_OPERATION_HISTORY": ("max_operation_history", int),

            # Performance configuration
            "MCP_QUERY_TIMEOUT_SECONDS": ("query_timeout_seconds", int),
            "MCP_SLOW_QUERY_THRESHOLD": ("slow_query_threshold", float),

            # Monitoring configuration
            "MCP_STATS_REPORT_INTERVAL": ("stats_report_interval", int),
            "MCP_HEALTH_CHECK_INTERVAL": ("health_check_interval", int),

            # Security configuration
            "MCP_ENABLE_AUTH": ("enable_auth", lambda x: x.lower() in ['true', '1', 'yes']),
            "MCP_AUTH_TOKEN": "auth_token",
            "MCP_ALLOWED_AGENTS": ("allowed_agents", lambda x: x.split(',')),
        }

        env_config = {}
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                if isinstance(config_key, tuple):
                    key, converter = config_key
                    try:
                        env_config[key] = converter(value)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Invalid value for {env_var}: {value}, error: {e}")
                else:
                    env_config[config_key] = value

        return env_config

    def _validate_config(self, config: MCPServerConfig) -> None:
        """Validate configuration values."""
        errors = []

        # Validate database configuration
        if config.connection_pool_size < 1:
            errors.append("connection_pool_size must be at least 1")

        # Validate cache configuration
        if config.default_cache_ttl < 1:
            errors.append("default_cache_ttl must be at least 1 second")
        if config.cache_cleanup_interval < 10:
            errors.append("cache_cleanup_interval must be at least 10 seconds")

        # Validate vector configuration
        if config.max_vector_results < 1:
            errors.append("max_vector_results must be at least 1")
        if not 0.0 <= config.default_similarity_threshold <= 1.0:
            errors.append("default_similarity_threshold must be between 0.0 and 1.0")

        # Validate event configuration
        if config.max_event_batch_size < 1:
            errors.append("max_event_batch_size must be at least 1")
        if config.event_retention_days < 1:
            errors.append("event_retention_days must be at least 1")

        # Validate codebase configuration
        if config.max_file_size_mb < 1:
            errors.append("max_file_size_mb must be at least 1")

        # Validate performance configuration
        if config.query_timeout_seconds < 1:
            errors.append("query_timeout_seconds must be at least 1")
        if config.slow_query_threshold < 0.1:
            errors.append("slow_query_threshold must be at least 0.1")

        # Validate monitoring configuration
        if config.stats_report_interval < 60:
            errors.append("stats_report_interval must be at least 60 seconds")
        if config.health_check_interval < 10:
            errors.append("health_check_interval must be at least 10 seconds")

        if errors:
            raise ValueError(f"Configuration validation errors: {'; '.join(errors)}")

    def save_config(self, config: MCPServerConfig) -> None:
        """Save configuration to file."""
        config_data = asdict(config)

        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            logger.info(f"Saved MCP config to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config to {self.config_file}: {e}")
            raise

    def get_config(self) -> MCPServerConfig:
        """Get the current configuration."""
        if self._config is None:
            return self.load_config()
        return self._config

    def reload_config(self) -> MCPServerConfig:
        """Reload configuration from file and environment."""
        self._config = None
        return self.load_config()


def create_example_config() -> Dict[str, Any]:
    """Create an example configuration file."""
    config = MCPServerConfig()
    return {
        "database": {
            "db_path": config.db_path,
            "connection_pool_size": config.connection_pool_size,
        },
        "cache": {
            "default_cache_ttl": config.default_cache_ttl,
            "cache_cleanup_interval": config.cache_cleanup_interval,
            "max_cache_size": config.max_cache_size,
        },
        "vector_memory": {
            "max_vector_results": config.max_vector_results,
            "default_similarity_threshold": config.default_similarity_threshold,
            "vector_embedding_dimension": config.vector_embedding_dimension,
        },
        "event_logging": {
            "max_event_batch_size": config.max_event_batch_size,
            "event_retention_days": config.event_retention_days,
        },
        "codebase_analysis": {
            "codebase_cache_ttl": config.codebase_cache_ttl,
            "max_file_size_mb": config.max_file_size_mb,
        },
        "devops_operations": {
            "devops_operation_ttl": config.devops_operation_ttl,
            "max_operation_history": config.max_operation_history,
        },
        "performance": {
            "query_timeout_seconds": config.query_timeout_seconds,
            "slow_query_threshold": config.slow_query_threshold,
        },
        "monitoring": {
            "stats_report_interval": config.stats_report_interval,
            "health_check_interval": config.health_check_interval,
        },
        "security": {
            "enable_auth": config.enable_auth,
            "auth_token": config.auth_token,
            "allowed_agents": config.allowed_agents,
        }
    }


def create_mcp_env_example() -> str:
    """Create environment variable examples for MCP configuration."""
    return """# Legion MCP Server Environment Configuration
# Override any configuration values using environment variables

# =============================================================================
# Database Configuration
# =============================================================================

# Database file path
# MCP_DB_PATH=memory/db/mcp_unified.db

# Connection pool size for database operations
# MCP_CONNECTION_POOL_SIZE=10

# =============================================================================
# Cache Configuration
# =============================================================================

# Default cache TTL in seconds (1 hour)
# MCP_DEFAULT_CACHE_TTL=3600

# Cache cleanup interval in seconds (5 minutes)
# MCP_CACHE_CLEANUP_INTERVAL=300

# Maximum number of cache entries
# MCP_MAX_CACHE_SIZE=10000

# =============================================================================
# Vector Memory Configuration
# =============================================================================

# Maximum number of vector results to return
# MCP_MAX_VECTOR_RESULTS=100

# Default similarity threshold for vector searches
# MCP_DEFAULT_SIMILARITY_THRESHOLD=0.8

# Vector embedding dimension (OpenAI default is 1536)
# MCP_VECTOR_EMBEDDING_DIMENSION=1536

# =============================================================================
# Event Logging Configuration
# =============================================================================

# Maximum number of events to return in a single batch
# MCP_MAX_EVENT_BATCH_SIZE=1000

# Number of days to retain events
# MCP_EVENT_RETENTION_DAYS=30

# =============================================================================
# Codebase Analysis Configuration
# =============================================================================

# Cache TTL for codebase analysis in seconds (24 hours)
# MCP_CODEBASE_CACHE_TTL=86400

# Maximum file size to analyze in MB
# MCP_MAX_FILE_SIZE_MB=10

# =============================================================================
# DevOps Operations Configuration
# =============================================================================

# TTL for DevOps operations in seconds (7 days)
# MCP_DEVOPS_OPERATION_TTL=604800

# Maximum number of operations to keep in history
# MCP_MAX_OPERATION_HISTORY=1000

# =============================================================================
# Performance Configuration
# =============================================================================

# Query timeout in seconds
# MCP_QUERY_TIMEOUT_SECONDS=30

# Slow query threshold in seconds
# MCP_SLOW_QUERY_THRESHOLD=1.0

# =============================================================================
# Monitoring Configuration
# =============================================================================

# Statistics report interval in seconds (5 minutes)
# MCP_STATS_REPORT_INTERVAL=300

# Health check interval in seconds (1 minute)
# MCP_HEALTH_CHECK_INTERVAL=60

# =============================================================================
# Security Configuration
# =============================================================================

# Enable authentication (true/false)
# MCP_ENABLE_AUTH=false

# Authentication token (if auth is enabled)
# MCP_AUTH_TOKEN=your-secret-token-here

# Comma-separated list of allowed agent names
# MCP_ALLOWED_AGENTS=doctor,researcher,architect

# =============================================================================
# Usage Examples
# =============================================================================

# Production configuration with authentication:
# MCP_ENABLE_AUTH=true
# MCP_AUTH_TOKEN=prod-secret-token-2024
# MCP_ALLOWED_AGENTS=doctor,researcher,architect,developer

# Development configuration with relaxed settings:
# MCP_DEFAULT_CACHE_TTL=1800
# MCP_CACHE_CLEANUP_INTERVAL=60
# MCP_STATS_REPORT_INTERVAL=60

# High-performance configuration:
# MCP_CONNECTION_POOL_SIZE=20
# MCP_MAX_CACHE_SIZE=50000
# MCP_QUERY_TIMEOUT_SECONDS=60
"""


# Global configuration manager
_config_manager: Optional[MCPConfigManager] = None


def get_config_manager(config_file: Optional[str] = None) -> MCPConfigManager:
    """Get the global configuration manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = MCPConfigManager(config_file)
    return _config_manager


def get_mcp_config() -> MCPServerConfig:
    """Get the current MCP configuration."""
    return get_config_manager().get_config()


def reload_mcp_config() -> MCPServerConfig:
    """Reload MCP configuration from file and environment."""
    return get_config_manager().reload_config()
