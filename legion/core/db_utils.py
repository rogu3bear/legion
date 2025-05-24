"""
Database utilities for Legion.

This module provides stubs for initializing the database and running migrations.
"""

import sqlite3
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "db"
SCHEMA_FILE = DB_DIR / "schema.sql"
MIGRATIONS_DIR = DB_DIR / "migrations"


def init_db(db_path: str) -> None:
    """Initialize the database using ``schema.sql`` if no tables exist."""

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        if not cursor.fetchall():
            with SCHEMA_FILE.open("r", encoding="utf-8") as f:
                schema_sql = f.read()
            cursor.executescript(schema_sql)
            conn.commit()
    finally:
        conn.close()


def run_migrations(db_path: str) -> None:
    """Apply SQL migrations located in the migrations directory."""

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY)"
        )
        cursor.execute(
            "SELECT COALESCE(MAX(version), 0) FROM schema_version"
        )
        row = cursor.fetchone()
        current_version = row[0] if row else 0

        migration_files: List[Path] = sorted(MIGRATIONS_DIR.glob("*.sql"))
        for file in migration_files:
            try:
                version = int(file.stem.split("_")[0])
                if version > current_version:
                    with file.open("r", encoding="utf-8") as f:
                        migration_sql = f.read()
                    cursor.executescript(migration_sql)
                    cursor.execute(
                        "INSERT INTO schema_version (version) VALUES (?)", (version,)
                    )
                    conn.commit()
            except (ValueError, IndexError):
                # Skip files that don't match the migration naming pattern
                continue
    finally:
        conn.close()
