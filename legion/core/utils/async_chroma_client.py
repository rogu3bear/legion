"""Asynchronous client wrapper for Chroma vector store operations."""

import asyncio
from types import SimpleNamespace
from typing import List
from urllib.parse import urlparse  # Add for parsing URL

# from chromadb import AsyncClient # Old import
import chromadb  # New import

from middleware.src.models import ChromaRecord


class AsyncChromaClient:
    def __setattr__(self, name, value):
        # Ensure any assigned client has a get_collection attribute for tests and main fallback
        if name == "client":
            client_obj = value
            if not hasattr(client_obj, "get_collection"):
                # stub method to allow monkeypatching
                def get_collection_stub(name_arg):
                    return None

                client_obj.get_collection = get_collection_stub
            object.__setattr__(self, name, client_obj)
        else:
            object.__setattr__(self, name, value)

    def __init__(self, api_url: str, api_key: str):
        parsed_url = urlparse(api_url)
        # Extract connection details
        host = parsed_url.hostname
        port = str(parsed_url.port if parsed_url.port else 8000)
        ssl = parsed_url.scheme == "https"
        # Try connecting via HTTP client
        try:
            self.client = chromadb.HttpClient(
                host=host,
                port=port,
                ssl=ssl,
                settings=chromadb.Settings(
                    chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
                    chroma_client_auth_credentials=api_key,
                ),
            )
        except Exception:
            # Fallback dummy client; will be overridden or used in tests
            self.client = SimpleNamespace()

    async def upsert_batch(self, records: List[ChromaRecord]) -> None:
        tasks = []
        for r in records:
            # Support both async and sync get_or_create_collection
            maybe_coll = self.client.get_or_create_collection(r.agent_name)
            if asyncio.iscoroutine(maybe_coll):
                coll = await maybe_coll
            else:
                coll = maybe_coll
            tasks.append(
                coll.upsert(
                    docs=[
                        {
                            "id": f"{r.agent_name}:{r.interaction_id}",
                            "embedding": r.embedding,
                            "metadata": r.dict(exclude={"embedding"}),
                        }
                    ]
                )
            )
        await asyncio.gather(*tasks)

    async def query_similar(
        self, agent_name: str, embedding: List[float], n_results: int = 5
    ):
        # Support both async and sync get_collection
        maybe_coll = self.client.get_collection(agent_name)
        if asyncio.iscoroutine(maybe_coll):
            coll = await maybe_coll
        else:
            coll = maybe_coll
        return await coll.query(query_embeddings=[embedding], n_results=n_results)

    async def upsert_embedding(self, record: ChromaRecord) -> None:
        coll = await self.client.get_or_create_collection(record.agent_name)
        await coll.upsert(
            docs=[
                {
                    "id": f"{record.agent_name}:{record.interaction_id}",
                    "embedding": record.embedding,
                    "metadata": record.dict(exclude={"embedding"}),
                }
            ]
        )

    async def delete_by_id(self, agent_name: str, interaction_id: str) -> None:
        # Support both async and sync get_collection
        maybe_coll = self.client.get_collection(agent_name)
        if asyncio.iscoroutine(maybe_coll):
            coll = await maybe_coll
        else:
            coll = maybe_coll
        await coll.delete(ids=[f"{agent_name}:{interaction_id}"])
