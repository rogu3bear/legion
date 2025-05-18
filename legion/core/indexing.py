"""Indexing utilities for Legion."""

import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)


def build_inverted_index(docs: List[Dict], field: str = "text") -> Dict[str, List[int]]:
    """
    Build a simple inverted index for a list of docs.
    Returns a dict: word -> list of doc indices.
    """
    logger.info(
        "Building simple inverted index", extra={"num_docs": len(docs), "field": field}
    )
    index: Dict[str, List[int]] = {}
    for i, doc in enumerate(docs):
        text = doc.get(field, "")
        words = set(re.findall(r"\w+", text.lower()))
        for word in words:
            index.setdefault(word, []).append(i)
    logger.info("Built index", extra={"index_size": len(index)})
    return index
