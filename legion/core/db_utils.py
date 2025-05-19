"""
Database utilities for Legion.

This module provides stubs for initializing the database and running migrations.
"""

import sqlite3


def init_db(db_path):
    """Initialize the database schema (stub)."""
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS example (id INTEGER PRIMARY KEY, data TEXT)"
        )
        conn.commit()
    finally:
        conn.close()


def run_migrations(db_path):
    """Run database migrations (stub)."""
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA user_version")
        version = cursor.fetchone()[0]
        if version < 1:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS migration_log (version INTEGER)"
            )
            cursor.execute("INSERT INTO migration_log(version) VALUES (1)")
            cursor.execute("PRAGMA user_version = 1")
        conn.commit()
    finally:
        conn.close()
