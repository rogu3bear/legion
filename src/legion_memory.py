"""
Legion agent persistent memory manager for agent state.
"""
import os
import json
import shutil
from datetime import datetime

class LegionAgentMemory:
    def __init__(self, agent_name, base_dir="memory"):
        self.agent_name = agent_name
        self.base_dir = os.path.join(base_dir, agent_name)
        self.data_file = os.path.join(self.base_dir, "memory.json")
        self.log_file = os.path.join(self.base_dir, "task_log.jsonl")
        self.docs_dir = os.path.join(self.base_dir, "docs")
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.base_dir, exist_ok=True)
        self._data = self._load_data()

    def _load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def save(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def log_task(self, task):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp": datetime.utcnow().isoformat(), **task}) + "\n")

    def get_task_log(self):
        if not os.path.exists(self.log_file):
            return []
        with open(self.log_file, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f]

    def save_document(self, name, content):
        # Versioned save
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        base = os.path.join(self.docs_dir, name)
        versioned = f"{base}.{ts}"
        with open(base, "w", encoding="utf-8") as f:
            f.write(content)
        shutil.copy(base, versioned)
        return versioned

    def get_document(self, name, version=None):
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
        return [f for f in os.listdir(self.docs_dir) if not f.startswith(".")]

    def list_versions(self, name):
        base = os.path.join(self.docs_dir, name)
        prefix = os.path.basename(base) + "."
        return [f for f in os.listdir(self.docs_dir) if f.startswith(prefix)]
