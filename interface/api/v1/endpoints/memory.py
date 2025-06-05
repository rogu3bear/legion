"""API endpoints for interacting with the Legion Memory system via the Orchestrator."""

import logging
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from interface import dependencies
from interface.api.v1.endpoints.system import _call_orchestrator
from interface.models.user import User
from interface.schemas.memory import (
    DocumentResponse,
    MemorySearchResultItem,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/documents", response_model=List[str], summary="List Memory Documents")
def list_memory_documents(
    current_user: User = Depends(dependencies.get_current_active_user)
) -> Any:
    """
    Retrieves a list of document names stored in the Legion Memory system.

    Sends a `memory_list_documents` command to the orchestrator.
    Requires an active user session.
    Raises HTTP 502 if communication with the orchestrator fails.
    """
    logger.info(f"User '{current_user.username}' requesting memory document list.")

    response_payload = _call_orchestrator(action="memory_list_documents")

    documents = response_payload.get("documents")
    if documents is None:
        logger.error(
            "Orchestrator response for memory_list_documents missing 'documents' key."
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY
            detail="Invalid response format from orchestrator."
        )

    return documents


@router.get(
    "/documents/{doc_name:path}"
    response_model=DocumentResponse
    summary="Get Memory Document"
)
def get_memory_document(
    doc_name: str = Path(
        ..., description="The full path/name of the document to retrieve."
    )
    version: Optional[str] = Query(
        None, description="Optional specific version of the document to retrieve."
    )
    current_user: User = Depends(dependencies.get_current_active_user)
) -> Any:
    """
    Retrieves a specific document (optionally a specific version) from the Legion Memory system.

    - **doc_name**: Path parameter allowing slashes in the document name.
    - **version**: Optional query parameter for a specific version ID.

    Sends a `memory_get_document` command to the orchestrator.
    Requires an active user session.
    Raises HTTP 404 if the document/version is not found.
    Raises HTTP 502 if communication with the orchestrator fails.
    """
    logger.info(
        f"User '{current_user.username}' requesting memory document '{doc_name}' (Version: {version})"
    )

    payload = {"document_name": doc_name}
    if version:
        payload["version"] = version

    response_payload = _call_orchestrator(action="memory_get_document", payload=payload)

    doc_content = response_payload.get("content")
    retrieved_name = response_payload.get("name", doc_name)
    retrieved_version = response_payload.get("version")

    if doc_content is None:
        if response_payload.get("status") == "not_found":
            logger.warning(
                f"Document '{doc_name}' (Version: {version}) not found in memory."
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND
                detail=f"Document '{doc_name}' not found."
            )
        else:
            logger.error(
                f"Orchestrator response for memory_get_document ('{doc_name}') missing 'content' key."
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY
                detail="Invalid response format from orchestrator."
            )

    return DocumentResponse(
        name=retrieved_name, content=doc_content, version=retrieved_version
    )


@router.get(
    "/agents/{agent_name}/search"
    response_model=List[MemorySearchResultItem]
    summary="Search Agent Memory"
)
def search_agent_memory(
    agent_name: str = Path(
        ..., description="The name of the agent whose memory to search."
    )
    query: str = Query(..., description="The text query to search for.")
    top_k: Optional[int] = Query(
        5, description="The maximum number of results to return.", ge=1, le=50
    )
    current_user: User = Depends(dependencies.get_current_active_user)
) -> Any:
    """
    Performs a semantic search within the vector memory of a specific agent.

    - **agent_name**: The target agent's name.
    - **query**: The search text.
    - **top_k**: Maximum number of results (default 5, max 50).

    Sends a `memory_search_agent` command to the orchestrator.
    Requires an active user session.
    Raises HTTP 404 if the agent is not found.
    Raises HTTP 502 if communication with the orchestrator fails.
    """
    logger.info(
        f"User '{current_user.username}' searching memory for agent '{agent_name}' with query '{query}' (top_k={top_k})."
    )

    payload = {"agent_name": agent_name, "query": query, "top_k": top_k}

    response_payload = _call_orchestrator(action="memory_search_agent", payload=payload)

    search_results = response_payload.get("results")

    if search_results is None:
        if response_payload.get("status") == "not_found":
            logger.warning(f"Agent '{agent_name}' not found for memory search.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND
                detail=f"Agent '{agent_name}' not found for memory search."
            )
        else:
            logger.error(
                f"Orchestrator response for memory_search_agent ('{agent_name}') missing 'results' key."
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY
                detail="Invalid response format from orchestrator for memory search."
            )

    # Assuming results are already in the correct format (e.g., List[MemorySearchResultItem])
    # Pydantic will validate based on the response_model
    return search_results


@router.get(
    "/search"
    response_model=List[MemorySearchResultItem]
    summary="Search Global Memory"
)
def search_global_memory(
    query: str = Query(..., description="The text query to search for.")
    top_k: Optional[int] = Query(
        5, description="The maximum number of results to return.", ge=1, le=50
    )
    current_user: User = Depends(dependencies.get_current_active_user)
) -> Any:
    """
    Performs a semantic search across all agent memories (if supported by the orchestrator).

    - **query**: The search text.
    - **top_k**: Maximum number of results (default 5, max 50).

    Sends a `memory_search_global` command to the orchestrator.
    Requires an active user session.
    Raises HTTP 502 if communication with the orchestrator fails.
    """
    logger.info(
        f"User '{current_user.username}' performing global memory search with query '{query}' (top_k={top_k})."
    )

    payload = {"query": query, "top_k": top_k}

    response_payload = _call_orchestrator(
        action="memory_search_global", payload=payload
    )

    search_results = response_payload.get("results")

    if search_results is None:
        logger.error(
            "Orchestrator response for memory_search_global missing 'results' key."
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY
            detail="Invalid response format from orchestrator for global memory search."
        )

    # Assuming results are in the correct format (List[MemorySearchResultItem])
    # Agent name might be included per result by the orchestrator
    return search_results
