"""Pydantic models for Memory API requests and responses."""

from typing import List, Optional

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    name: str = Field(..., description="Name or path of the document.")
    content: str = Field(..., description="Content of the document.")
    version: Optional[str] = Field(
        None, description="Version identifier of the document, if available."
    )
    message: Optional[str] = Field(
        None, description="Optional status or error message."
    )


class MemorySearchRequest(BaseModel):
    query: str = Field(..., description="The text query to search for in memory.")
    top_k: Optional[int] = Field(
        5, description="Number of top results to return (default 5)."
    )


class MemorySearchResultItem(BaseModel):
    text: str = Field(..., description="Text content of the memory search result.")
    score: Optional[float] = Field(
        None, description="Similarity score for the result, if provided."
    )
    metadata: Optional[dict] = Field(
        None, description="Additional metadata for the result, if available."
    )


class MemorySearchResponse(BaseModel):
    results: List[MemorySearchResultItem] = Field(
        ..., description="List of memory search results."
    )
    query: str = Field(..., description="The original search query.")
    agent_name: Optional[str] = Field(
        None, description="Name of the agent whose memory was searched, if applicable."
    )
    message: Optional[str] = Field(
        None, description="Optional status or error message."
    )
