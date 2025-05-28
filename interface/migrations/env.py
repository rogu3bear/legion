"""Alembic environment configuration for Legion Interface database."""

import sys
from logging.config import fileConfig
from os import environ  # Added for environment variable handling
from pathlib import Path

from alembic import context
from sqlalchemy import (  # Added for explicit engine creation
    create_engine
)

# --- Custom Imports for Legion Interface --- START ---
# Ensure the project root is in sys.path to find 'interface' package
script_dir = Path(__file__).parent.parent  # migrations -> interface
project_root = script_dir.parent  # interface -> project root
sys.path.insert(0, str(project_root))

# Import Base from the interface db setup
from interface.db.base import Base

# Import all models to be recognized by Alembic autogenerate
from interface.models import *  # Ensure all models are imported

# --- Custom Imports for Legion Interface --- END ---

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add model's MetaData object for 'autogenerate' support
target_metadata = Base.metadata


# Ensure the database directory exists before connecting
def ensure_db_directory_exists():
    url = environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///./db/legion_ui.db")
    if url and url.startswith("sqlite:///"):
        # Construct absolute path relative to the ini file's location (interface/)
        # ini_path = Path(config.config_file_name).parent
        # db_relative_path = url.replace('sqlite:///', '')
        # db_path = (ini_path / db_relative_path).resolve()

        # --- Alternative: Construct path relative to this env.py ---
        # db_relative_path = url.replace('sqlite:///', '') # e.g., 'db/interface.db'
        # migrations_dir = Path(__file__).parent # interface/migrations
        # interface_dir = migrations_dir.parent # interface/
        # db_path = (interface_dir / db_relative_path).resolve()

        # --- Simplest: Use absolute path from project root perspective ---
        # Assumes alembic command is run from project root
        db_relative_to_root = url.replace("sqlite:///", "")  # e.g., db/interface.db
        db_path = project_root / "interface" / db_relative_to_root

        print(f"[Alembic Env] Ensuring database directory exists for: {db_path}")
        db_path.parent.mkdir(parents=True, exist_ok=True)
    elif not url:
        print("[Alembic Env] Warning: sqlalchemy.url not found in config.")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    ensure_db_directory_exists()
    url = environ.get(
        "SQLALCHEMY_DATABASE_URI", "sqlite+aiosqlite:///./db/legion_ui.db"
    )
    context.configure(
        url=url
        target_metadata=target_metadata
        literal_binds=True
        dialect_opts={"paramstyle": "named"}
        compare_type=True,  # Added to detect column type changes
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    ensure_db_directory_exists()
    connectable = create_engine(
        environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///memory/db/legion.db")
        echo=True
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection
            target_metadata=target_metadata
            compare_type=True,  # Added to detect column type changes
        )

        with context.begin_transaction():
            context.run_migrations()


# Run migrations based on mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
