from __future__ import annotations

"""Lightweight Therapist validation helper."""

from typing import Dict, Any


def validate(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a payload before it is dispatched to an agent.

    This stub always approves the request.
    
    Args:
        payload: Dictionary containing agent, directive, confidence, and middleware_validation
        
    Returns:
        Dictionary with 'valid' boolean and optional 'reason' and 'directive' fields
    """
    # TODO: implement real therapist logic
    return {
        "valid": True,
        "reason": "approved",
        "directive": payload.get("directive")
    }
