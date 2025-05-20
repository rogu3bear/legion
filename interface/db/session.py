"""Database session management."""

from typing import Generator

from interface.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# Use check_same_thread=False only for SQLite
connect_args = (
    {"check_same_thread": False}
    if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Alias used in test suite for clarity
TestingSessionLocal = SessionLocal  # Provides same configured sessionmaker

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency to get a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
