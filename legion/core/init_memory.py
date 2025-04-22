"""
Stub memory initialization script for Legion.
Creates memory/db/legion.db if missing.
"""
import os
from pathlib import Path

def main():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'memory', 'db', 'legion.db')
    db_path = os.path.abspath(db_path)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if not os.path.exists(db_path):
        Path(db_path).touch()
        print(f"[init_memory] Created {db_path}")
    else:
        print(f"[init_memory] {db_path} already exists.")

    # Create empty task log file
    task_log_path = Path(os.path.dirname(db_path), "logs", "task_log.jsonl")
    task_log_path.parent.mkdir(parents=True, exist_ok=True)
    if not task_log_path.exists():
        task_log_path.touch()

    # Create/initialize SQLite database

if __name__ == "__main__":
    main() 