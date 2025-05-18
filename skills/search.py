"""Search skill for Legion."""

from typing import Any, Dict, List

import numpy as np


def vector_search(
    query_embedding: List[float], docs: List[Dict[str, Any]], top_k: int = 3
) -> List[Dict[str, Any]]:
    """
    Perform a vector similarity search over docs.
    Each doc must have an 'embedding' key (list of floats).
    Returns top_k docs sorted by cosine similarity.
    """
    if not docs or not query_embedding:
        return []

    def cosine(a, b):
        a = np.array(a)
        b = np.array(b)
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    scored = [
        (cosine(query_embedding, doc["embedding"]), doc)
        for doc in docs
        if "embedding" in doc
    ]
    scored.sort(reverse=True, key=lambda x: x[0])
    return [doc for _, doc in scored[:top_k]]
