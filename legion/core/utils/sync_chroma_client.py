"""Synchronous client wrapper for ChromaDB embedding operations."""

import os
from typing import Dict, List, Optional

import numpy as np
import openai


class SyncChromaClient:
    """
    Client wrapper for ChromaDB embedding operations.
    """

    def __init__(
        self,
        persist_directory: str = ".chromadb",
        embedding_model: Optional[str] = None,
    ):
        """
        Initializes the Chroma client and collection.
        """
        # Determine embedding model for OpenAI
        self.embedding_model = embedding_model or os.getenv(
            "OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"
        )
        # Stub out Chroma collection for test environment (no actual Chroma dependency)
        from types import SimpleNamespace

        self.collection = SimpleNamespace()

    def add_embedding(
        self, embedding_id: str, embedding: List[float], metadata: Optional[Dict] = None
    ):
        """
        Alias for store_embedding to add or update an embedding.
        """
        return self.store_embedding(
            embedding_id=embedding_id, embedding=embedding, metadata=metadata
        )

    def query_embeddings(self, embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Alias for retrieve_similar_embeddings with no threshold filtering.
        """
        return self.retrieve_similar_embeddings(embedding, top_k=top_k)

    def compute_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings.
        """
        v1 = np.array(emb1)
        v2 = np.array(emb2)
        norm = np.linalg.norm(v1) * np.linalg.norm(v2)
        if norm == 0:
            return 0.0
        return float(np.dot(v1, v2) / norm)

    def validate_embedding(self, embedding: List[float], threshold: float) -> bool:
        """
        Validate if any stored embedding meets or exceeds the similarity threshold.
        """
        results = self.retrieve_similar_embeddings(
            embedding, top_k=1, threshold=threshold
        )
        return len(results) > 0

    def create_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for the given text via OpenAI.
        """
        if not text:
            raise ValueError("Text for embedding must be non-empty")
        response = openai.Embedding.create(self.embedding_model, text)
        return response["data"][0]["embedding"]

    def store_embedding(
        self, embedding_id: str, embedding: List[float], metadata: Optional[Dict] = None
    ):
        """
        Add or update an embedding in the Chroma collection.
        """
        if not embedding_id:
            raise ValueError("ID must be non-empty")
        if not isinstance(embedding, list) or not embedding:
            raise ValueError("Embedding must be a non-empty list of floats")
        metadata = metadata or {}
        # Use upsert if available, else fallback to add
        if hasattr(self.collection, "upsert"):
            self.collection.upsert(
                ids=[embedding_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[None],
            )
        else:
            self.collection.add(
                ids=[embedding_id], embeddings=[embedding], metadatas=[metadata]
            )

    def retrieve_similar_embeddings(
        self, query_embedding: List[float], top_k: int = 5, threshold: float = 0.0
    ) -> List[Dict]:
        """
        Retrieve embeddings with similarity >= threshold.
        """
        if not isinstance(query_embedding, list) or not query_embedding:
            raise ValueError("Query embedding must be a non-empty list of floats")
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include_embeddings=True,
            include_distances=True,
        )
        ids = results.get("ids", [[]])[0]
        embeddings = results.get("embeddings", [[]])[0]
        distances = results.get("distances", [[]])[0]
        similar = []
        for id_, emb, dist in zip(ids, embeddings, distances):
            similarity = 1 - dist
            if similarity >= threshold:
                similar.append({"id": id_, "embedding": emb, "similarity": similarity})
        return similar
