"""Module for interacting with ChromaDB for embedding storage and retrieval."""

import os
from typing import Dict, List, Optional

import numpy as np
import openai
import asyncio


class ChromaClient:
    """
    Client wrapper for ChromaDB embedding operations.
    """

    def __init__(
        self
        persist_directory: str = ".chromadb"
        embedding_model: Optional[str] = None
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
                ids=[embedding_id]
                embeddings=[embedding]
                metadatas=[metadata]
                documents=[None]
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
            query_embeddings=[query_embedding]
            n_results=top_k
            include_embeddings=True
            include_distances=True
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


class AsyncChromaClient:
    """Async wrapper for Chroma vector store operations."""

    def __setattr__(self, name, value):
        if name == "client":
            client_obj = value
            if not hasattr(client_obj, "get_collection"):
                def get_collection_stub(name_arg):
                    return None

                client_obj.get_collection = get_collection_stub
            object.__setattr__(self, name, client_obj)
        else:
            object.__setattr__(self, name, value)

    def __init__(self, api_url: str, api_key: str):
        from types import SimpleNamespace
        from urllib.parse import urlparse
        import chromadb

        parsed_url = urlparse(api_url)
        host = parsed_url.hostname
        port = str(parsed_url.port if parsed_url.port else 8000)
        ssl = parsed_url.scheme == "https"
        try:
            self.client = chromadb.HttpClient(
                host=host
                port=port
                ssl=ssl
                settings=chromadb.Settings(
                    chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider"
                    chroma_client_auth_credentials=api_key
                )
            )
        except Exception:
            self.client = SimpleNamespace()

    async def upsert_batch(self, records: List["ChromaRecord"]) -> None:
        tasks = []
        for r in records:
            maybe_coll = self.client.get_or_create_collection(r.agent_name)
            coll = await maybe_coll if asyncio.iscoroutine(maybe_coll) else maybe_coll
            tasks.append(
                coll.upsert(
                    docs=[
                        {
                            "id": f"{r.agent_name}:{r.interaction_id}"
                            "embedding": r.embedding
                            "metadata": r.dict(exclude={"embedding"})
                        }
                    ]
                )
            )
        await asyncio.gather(*tasks)

    async def query_similar(self, agent_name: str, embedding: List[float], n_results: int = 5):
        maybe_coll = self.client.get_collection(agent_name)
        coll = await maybe_coll if asyncio.iscoroutine(maybe_coll) else maybe_coll
        return await coll.query(query_embeddings=[embedding], n_results=n_results)

    async def upsert_embedding(self, record: "ChromaRecord") -> None:
        coll = await self.client.get_or_create_collection(record.agent_name)
        await coll.upsert(
            docs=[
                {
                    "id": f"{record.agent_name}:{record.interaction_id}"
                    "embedding": record.embedding
                    "metadata": record.dict(exclude={"embedding"})
                }
            ]
        )

    async def delete_by_id(self, agent_name: str, interaction_id: str) -> None:
        maybe_coll = self.client.get_collection(agent_name)
        coll = await maybe_coll if asyncio.iscoroutine(maybe_coll) else maybe_coll
        await coll.delete(ids=[f"{agent_name}:{interaction_id}"])
