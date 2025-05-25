"""Dependency Injection Container for Legion."""

from typing import Any, Dict, Type, TypeVar

from core.interfaces import ILLMClient, IMemoryManager, IStateManager

T = TypeVar("T")


class DIContainer:
    """A simple dependency injection container for managing service instances."""

    def __init__(self):
        self._instances: Dict[Type[Any], Any] = {}
        self._factories: Dict[Type[Any], callable] = {}

    def register_instance(self, service_type: Type[T], instance: T) -> None:
        """Register a pre-created instance of a service."""
        self._instances[service_type] = instance

    def register_factory(self, service_type: Type[T], factory: callable) -> None:
        """Register a factory function for creating a service instance."""
        self._factories[service_type] = factory

    def get(self, service_type: Type[T]) -> T:
        """Retrieve a service instance by its type."""
        if service_type in self._instances:
            return self._instances[service_type]
        if service_type in self._factories:
            instance = self._factories[service_type]()
            self._instances[service_type] = instance
            return instance
        raise KeyError(
            f"Service {service_type.__name__} not registered in DI container"
        )

    def clear(self) -> None:
        """Clear all registered instances and factories (useful for tests)."""
        self._instances.clear()
        self._factories.clear()


# Global container instance for convenience
container = DIContainer()


# Helper functions for common services
def get_llm_client() -> ILLMClient:
    """Get the registered LLM client."""
    return container.get(ILLMClient)


def get_state_manager() -> IStateManager:
    """Get the registered state manager."""
    return container.get(IStateManager)


def get_memory_manager() -> IMemoryManager:
    """Get the registered memory manager."""
    return container.get(IMemoryManager)


# Default service registrations
import os
from core.utils.llm_client import LLMClient
from core.state import StateManager

# Use mode-switching client if LLM_MODE is set, otherwise use legacy client
if os.getenv("LLM_MODE"):
    from legion.core.llm_mode_client import create_mode_switching_llm_client
    container.register_factory(ILLMClient, create_mode_switching_llm_client)
else:
    container.register_factory(ILLMClient, LLMClient)

container.register_factory(IStateManager, StateManager)
