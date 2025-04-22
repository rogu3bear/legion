"""
Legion agent persistent memory manager for agent state.
"""

import json
import logging
import math
import os
import shutil
import sqlite3
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class LegionAgentMemory:
    def __init__(self, agent_name: str, base_dir: str = "memory") -> None:
        """Initialize memory for a specific agent."""
        logger.info("Initializing LegionAgentMemory", extra={"agent_name": agent_name, "base_dir": base_dir})
        self.agent_name = agent_name
        self.base_dir = os.path.join(base_dir, agent_name)
        self.data_file = os.path.join(self.base_dir, "memory.json")
        self.log_file = os.path.join(self.base_dir, "task_log.jsonl")
        self.docs_dir = os.path.join(self.base_dir, "docs")
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.base_dir, exist_ok=True)
        self.db_path = os.path.join(os.path.dirname(__file__), "db", "legion.db")
        self._ensure_db()
        self._data = self._load_data()

    def _ensure_db(self):
        """Ensures the SQLite DB and task_log table exist."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS task_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        agent_name TEXT,
                        task_data TEXT
                    )"""
        )
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
        c.execute(
            "INSERT INTO task_log (agent_name, task_data) VALUES (?, ?)",
            (self.agent_name, json.dumps(task)),
        )
        conn.commit()
        conn.close()

    def get_task_log(self):
        """Retrieves the agent's task log from the DB."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "SELECT task_data FROM task_log WHERE agent_name = ?", (self.agent_name,)
        )
        rows = c.fetchall()
        conn.close()
        return [json.loads(row[0]) for row in rows]

    def save_document(self, name, content):
        """Saves a versioned document for the agent."""
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
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

    @staticmethod
    def _vector_store_path(agent_name, base_dir="memory"):
        """Returns the path to the agent's vector store JSONL file."""
        return os.path.join(base_dir, agent_name, "vector_store.jsonl")

    @staticmethod
    def _cosine_similarity(vec1, vec2):
        """Compute cosine similarity between two vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    @classmethod
    def retrieve_memories(cls, agent_name, embedding, top_k, base_dir="memory"):
        """
        Loads or creates the vector index for that agent. Returns up to topK text snippets most similar to the embedding.
        Returns an empty list if nothing is there.
        """
        path = cls._vector_store_path(agent_name, base_dir)
        if not os.path.exists(path):
            return []
        try:
            items = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        if "embedding" in obj and "text" in obj:
                            sim = cls._cosine_similarity(embedding, obj["embedding"])
                            items.append((sim, obj["text"]))
                    except Exception:
                        continue
            items.sort(reverse=True, key=lambda x: x[0])
            return [text for _, text in items[:top_k]]
        except Exception as e:
            logging.error(
                f"[LegionAgentMemory] Failed to retrieve memories for {agent_name}: {e}"
            )
            return []

    @classmethod
    def store_memories(cls, agent_name, snippets, base_dir="memory"):
        """
        Upserts the given snippets into the agent's vector store. Retries once on failure, logs error if still failing.
        Each snippet should be a dict with 'text' and 'embedding'.
        """
        path = cls._vector_store_path(agent_name, base_dir)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        def _write():
            with open(path, "a", encoding="utf-8") as f:
                for snip in snippets:
                    if (
                        isinstance(snip, dict)
                        and "text" in snip
                        and "embedding" in snip
                    ):
                        f.write(json.dumps(snip) + "\n")

        try:
            _write()
        except Exception as e:
            logging.warning(
                f"[LegionAgentMemory] Store failed for {agent_name}, retrying: {e}"
            )
            try:
                _write()
            except Exception as e2:
                logging.error(
                    f"[LegionAgentMemory] Store failed again for {agent_name}: {e2}"
                )

    def add_raw_memory(self, text: str, metadata: dict = None):
        """Adds raw text to the memory, potentially for later processing."""
        metadata = metadata or {}
        metadata["source_type"] = "raw_text"
        # Simple timestamped filename for raw dumps
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S_%f") # Use timezone.utc, add microseconds
        raw_path = self.memory_dir / "raw"
        raw_path.mkdir(exist_ok=True)
        with open(raw_path / f"raw_{ts}.txt", "w") as f:
            f.write(text)  # Added file write logic
            # Optionally, write metadata as JSON header or separate file
            logging.info(f"Saved raw memory to raw_{ts}.txt")


def retrieve_memories(agent_name, embedding, top_k, base_dir="memory"):
    return LegionAgentMemory.retrieve_memories(
        agent_name, embedding, top_k, base_dir=base_dir
    )


def store_memories(agent_name, snippets, base_dir="memory"):
    return LegionAgentMemory.store_memories(agent_name, snippets, base_dir=base_dir)
