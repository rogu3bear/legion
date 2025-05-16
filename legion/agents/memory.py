"""
Memory management for Legion agents.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class LegionAgentMemory:
    """Memory management for Legion agents."""

    def __init__(self, agent_name: str, memory_dir: Optional[str] = None):
        """Initialize agent memory.

        Args:
            agent_name: Name of the agent
            memory_dir: Directory to store memory files (defaults to ./memory)
        """
        self.agent_name = agent_name
        self.memory_dir = Path(memory_dir or "./memory")
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.memory_dir / f"{agent_name}_memory.json"
        self._load_memory()

    def _load_memory(self) -> None:
        """Load memory from file."""
        if self.memory_file.exists():
            with open(self.memory_file) as f:
                self.memory = json.load(f)
        else:
            self.memory = {}

    def _save_memory(self) -> None:
        """Save memory to file."""
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from memory.

        Args:
            key: Memory key
            default: Default value if key not found

        Returns:
            Value from memory or default
        """
        return self.memory.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a value in memory.

        Args:
            key: Memory key
            value: Value to store
        """
        self.memory[key] = value
        self._save_memory()

    def delete(self, key: str) -> None:
        """Delete a value from memory.

        Args:
            key: Memory key to delete
        """
        if key in self.memory:
            del self.memory[key]
            self._save_memory()

    def clear(self) -> None:
        """Clear all memory."""
        self.memory = {}
        self._save_memory()

    def get_all(self) -> Dict[str, Any]:
        """Get all memory.

        Returns:
            Complete memory dictionary
        """
        return self.memory.copy()

    def log_task(self, task: Dict[str, Any]) -> None:
        """Log a task to memory.

        Args:
            task: Task data to log
        """
        tasks = self.get("tasks", [])
        tasks.append(task)
        self.set("tasks", tasks)

    def get_task_log(self) -> List[Dict[str, Any]]:
        """Get task log.

        Returns:
            List of logged tasks
        """
        return self.get("tasks", [])
