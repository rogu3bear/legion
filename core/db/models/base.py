"""Base model configuration and shared utilities for Legion database models.

This module provides the base SQLAlchemy configuration and shared functionality
used across all Legion database models. It includes connection management,
session handling, and common utility functions.
"""

from typing import Any, Dict, Optional, Type, TypeVar

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

# Type variable for model classes
ModelType = TypeVar("ModelType", bound="Base")

# Shared metadata object for schema-wide operations
metadata = MetaData()

# Create declarative base class
Base = declarative_base(metadata=metadata)


class DatabaseConfig:
    """Configuration for database connection and session management."""

    _engine = None
    _session_factory = None

    @classmethod
    def init_db(cls, db_url: str = "sqlite:///memory/db/legion.db") -> None:
        """Initialize database connection and session factory.

        Args:
            db_url: Database connection URL, defaults to SQLite
        """
        cls._engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
        )
        cls._session_factory = sessionmaker(bind=cls._engine, expire_on_commit=False)

    @classmethod
    def get_session(cls) -> Session:
        """Get a new database session.

        Returns:
            Session: New SQLAlchemy session instance

        Raises:
            RuntimeError: If database not initialized
        """
        if cls._session_factory is None:
            raise RuntimeError("Database not initialized. Call init_db first.")
        return cls._session_factory()

    @classmethod
    def create_all(cls) -> None:
        """Create all database tables."""
        if cls._engine is None:
            raise RuntimeError("Database not initialized. Call init_db first.")
        Base.metadata.create_all(cls._engine)


class BaseModel(Base):
    """Abstract base class for all Legion models.

    Provides common functionality and utilities used across all models.
    """

    __abstract__ = True

    @classmethod
    def get_by_id(
        cls: Type[ModelType], session: Session, id: int
    ) -> Optional[ModelType]:
        """Get model instance by ID.

        Args:
            session: Database session
            id: Primary key to look up

        Returns:
            Optional[ModelType]: Model instance if found, None otherwise
        """
        return session.query(cls).filter(cls.id == id).first()

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of model
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
