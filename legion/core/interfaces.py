"""Interfaces for Legion core services, enabling dependency injection."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ILLMClient(ABC):
    """Interface for LLM client implementations."""

    @abstractmethod
    def call(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call the LLM with a list of messages and return the response."""
        pass

    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """Generate an embedding for the given text."""
        pass


class IStateManager(ABC):
    """Interface for state management implementations."""

    @abstractmethod
    def log_task(self, task: Dict[str, Any]) -> None:
        """Log a task or event to persistent state."""
        pass

    @abstractmethod
    def get_state(self, key: str) -> Optional[Any]:
        """Retrieve a state value by key."""
        pass

    @abstractmethod
    def set_state(self, key: str, value: Any) -> None:
        """Set a state value by key."""
        pass


class IMemoryManager(ABC):
    """Interface for memory management implementations."""

    @abstractmethod
    def log_task(self, task: Dict[str, Any]) -> None:
        """Log a task or event to memory."""
        pass

    @abstractmethod
    def store_memory(
        self, id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store a memory entry with optional metadata."""
        pass

    @abstractmethod
    def retrieve_memories(
        self,
        agent_name: str,
        embedding: List[float],
        top_k: int,
        category: Optional[str] = None,
    ) -> List[str]:
        """Retrieve memories based on embedding similarity."""
        pass

    @abstractmethod
    def store_memories(
        self, agent_name: str, snippets: List[Dict[str, Any]], base_dir: str = "memory"
    ) -> None:
        """Store multiple memory snippets with embeddings."""
        pass
