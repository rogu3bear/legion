"""
Temporary shim package for Legion reorganization.

This module re-exports core utilities to maintain compatibility
during the reorganization process. Will be removed in PR-D.

Part of Legion Re-org Safety Blueprint - Phase 2
"""

# Re-export core utilities from their new locations
try:
    from core.utils.chroma_client import ChromaClient
    from core.utils.file_operations import (
        get_all_prompts,
        list_available_agents,
        load_prompt,
        save_prompt,
    )
    from core.utils.indexing import placeholder_indexing
    from core.utils.network import fetch_with_retries
except ImportError:
    # Fallback during transition
    def fetch_with_retries(*args, **kwargs):
        """Placeholder during reorganization."""
        raise NotImplementedError("Core utilities not yet moved")

    def placeholder_indexing(*args, **kwargs):
        """Placeholder during reorganization."""
        raise NotImplementedError("Core utilities not yet moved")

    def load_prompt(*args, **kwargs):
        """Placeholder during reorganization."""
        raise NotImplementedError("File operations not yet moved")

    def save_prompt(*args, **kwargs):
        """Placeholder during reorganization."""
        raise NotImplementedError("File operations not yet moved")

    def list_available_agents(*args, **kwargs):
        """Placeholder during reorganization."""
        raise NotImplementedError("File operations not yet moved")

    def get_all_prompts(*args, **kwargs):
        """Placeholder during reorganization."""
        raise NotImplementedError("File operations not yet moved")

    class ChromaClient:
        """Placeholder during reorganization."""

        def __init__(self, *args, **kwargs):
            raise NotImplementedError("Core utilities not yet moved")


__all__ = [
    "ChromaClient",
    "fetch_with_retries",
    "get_all_prompts",
    "list_available_agents",
    "load_prompt",
    "placeholder_indexing",
    "save_prompt",
]
