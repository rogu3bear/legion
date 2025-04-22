"""Core indexing utilities for Legion."""

import re
from typing import Dict, List

def index_text(text: str) -> List[str]:
    """Placeholder for text indexing logic."""
    # Simple split for now
    return re.findall(r'\b\w+\b', text.lower())

def render_feed_item(agent_name: str, message: str, fields: List = None) -> Dict:
    """Placeholder for rendering a feed item (e.g., Discord embed)."""
    return {
        "title": agent_name,
        "description": message,
        "fields": fields or []
    }

def extract_keywords(text: str) -> List[str]:
    """Extracts keywords from text (stub)."""
    # Simple placeholder
    return re.findall(r'\b\w{4,}\b', text.lower()) # Example: find words >= 4 chars 