"""API endpoints for system-level information and control via the Orchestrator."""

import logging
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from interface import dependencies
from interface.models.user import User
from interface.orchestrator_comm import send_request

logger = logging.getLogger(__name__)
router = APIRouter()


def _call_orchestrator(
    action: str, payload: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Internal helper to send requests to the Orchestrator via ZeroMQ REQ/REP.

    Handles request construction, communication, and basic error checking.
    Raises appropriate HTTPErrors for communication failures or orchestrator errors.
    """
    command = {"action": action, "request_id": str(uuid.uuid4())}
    if payload:
        command.update(payload)

    try:
        response_data = send_request(command)
    except Exception as e:
        logger.error(
            f"Unexpected error calling send_request for action '{action}': {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error communicating with orchestrator.",
        )

    if response_data is None:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="No response received from orchestrator or communication failed.",
        )

    # Response payload is nested under "response" key in the ZMQ reply
    response_payload = response_data.get("response", {})
    if response_payload.get("status") == "error":
        detail = response_payload.get("detail", "Unknown orchestrator error")
        logger.warning(f"Orchestrator returned error for action '{action}': {detail}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Orchestrator error: {detail}",
        )

    # Return the actual payload nested within the response
    return response_payload


@router.get("/status", response_model=Dict[str, Any], summary="Get System Status")
def get_system_status(
    current_user: User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Retrieves the current overall system status from the Legion Orchestrator.

    This typically includes orchestrator status and a summary of agent health.
    Requires an active user session.
    """
    logger.info(f"User '{current_user.username}' requesting system status.")
    return _call_orchestrator(action="status")


@router.get("/metrics", response_model=Dict[str, Any], summary="Get System Metrics")
def get_system_metrics(
    current_user: User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Retrieves system performance and operational metrics from the Orchestrator.

    The specific metrics returned are determined by the Orchestrator's implementation.
    Requires an active user session.
    """
    logger.info(f"User '{current_user.username}' requesting system metrics.")
    return _call_orchestrator(action="metrics")


@router.get("/logs", response_model=Dict[str, Any], summary="Get System Logs")
def get_system_logs(
    # TODO: Add query parameters for filtering (e.g., level, agent, limit)
    current_user: User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Retrieves recent system logs from the Legion Orchestrator.

    Future enhancements may include filtering options.
    Requires an active user session.
    """
    logger.info(f"User '{current_user.username}' requesting system logs.")
    # TODO: Pass filter parameters in payload if implemented
    return _call_orchestrator(action="logs")


@router.get(
    "/memory/stats", response_model=Dict[str, Any], summary="Get Memory Statistics"
)
def get_memory_stats(
    current_user: User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Retrieves usage statistics for the Legion memory system via the Orchestrator.

    Requires an active user session.
    """
    logger.info(f"User '{current_user.username}' requesting memory stats.")
    return _call_orchestrator(action="memory_stats")
