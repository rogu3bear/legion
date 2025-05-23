from __future__ import annotations

"""Lightweight Therapist validation helper."""

from typing import Tuple, Dict, Any


def validate(payload: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate a payload before it is dispatched to an agent.

    This stub always approves the request.
    """
    # TODO: implement real therapist logic
    return True, "approved"
