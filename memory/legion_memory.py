"""
Legion agent persistent memory manager for agent state.
"""
import os
import json
import shutil
import sqlite3
from datetime import datetime

class LegionAgentMemory:
    def __init__(self, agent_name, base_dir="memory"):
        """Initializes persistent memory for an agent."""
        self.agent_name = agent_name
        self.base_dir = os.path.join(base_dir, agent_name)
        self.data_file = os.path.join(self.base_dir, "memory.json")
        self.log_file = os.path.join(self.base_dir, "task_log.jsonl")
        self.docs_dir = os.path.join(self.base_dir, "docs")
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.base_dir, exist_ok=True)
        self.db_path = os.path.join(os.path.dirname(__file__), 'db', 'legion.db')
        self._ensure_db()
        self._data = self._load_data()

    def _ensure_db(self):
        """Ensures the SQLite DB and task_log table exist."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS task_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        agent_name TEXT,
                        task_data TEXT
                    )''')
        conn.commit()
        conn.close()

    def _load_data(self):
        """Loads agent memory data from disk."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def get(self, key):
        """Gets a value from memory."""
        return self._data.get(key)

    def set(self, key, value):
        """Sets a value in memory and saves."""
        self._data[key] = value
        self.save()

    def save(self):
        """Saves memory data to disk."""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def log_task(self, task):
        """Logs a task to the SQLite DB."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO task_log (agent_name, task_data) VALUES (?, ?)',
                  (self.agent_name, json.dumps(task)))
        conn.commit()
        conn.close()

    def get_task_log(self):
        """Retrieves the agent's task log from the DB."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT task_data FROM task_log WHERE agent_name = ?', (self.agent_name,))
        rows = c.fetchall()
        conn.close()
        return [json.loads(row[0]) for row in rows]

    def save_document(self, name, content):
        """Saves a versioned document for the agent."""
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        base = os.path.join(self.docs_dir, name)
        versioned = f"{base}.{ts}"
        with open(base, "w", encoding="utf-8") as f:
            f.write(content)
        shutil.copy(base, versioned)
        return versioned

    def get_document(self, name, version=None):
        """Retrieves a document (optionally by version)."""
        base = os.path.join(self.docs_dir, name)
        if version:
            path = f"{base}.{version}"
        else:
            path = base
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def list_documents(self):
        """Lists all documents for the agent."""
        return [f for f in os.listdir(self.docs_dir) if not f.startswith(".")]

    def list_versions(self, name):
        """Lists all versions of a document."""
        base = os.path.join(self.docs_dir, name)
        prefix = os.path.basename(base) + "."
        return [f for f in os.listdir(self.docs_dir) if f.startswith(prefix)]
