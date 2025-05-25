"""
Temporary shim package for Legion reorganization.

This module re-exports core utilities to maintain compatibility
during the reorganization process. Will be removed in PR-D.

Part of Legion Re-org Safety Blueprint - Phase 2
"""

# Re-export core utilities from their new locations
try:
    from core.utils.network import fetch_with_retries
    from core.utils.indexing import placeholder_indexing
    from core.utils.chroma_client import ChromaClient
except ImportError:
    # Fallback during transition
    def fetch_with_retries(*args, **kwargs):
        """Placeholder during reorganization."""
        raise NotImplementedError("Core utilities not yet moved")
    
    def placeholder_indexing(*args, **kwargs):
        """Placeholder during reorganization."""
        raise NotImplementedError("Core utilities not yet moved")
    
    class ChromaClient:
        """Placeholder during reorganization."""
        def __init__(self, *args, **kwargs):
            raise NotImplementedError("Core utilities not yet moved")

__all__ = ['fetch_with_retries', 'placeholder_indexing', 'ChromaClient']
