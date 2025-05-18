"""Hallucination guard for agent responses.

This module provides ``guard_response`` which performs a minimal
confidence check on an agent's output.  The logic mirrors the
"Hallucination Guard" section described in ``docs/middleware.md`` and
emits a message to the ``agent-feed`` when a response falls below the
configured threshold.
"""

import logging

from legion.utils.agent_feed import post_agent_feed

logger = logging.getLogger(__name__)


def guard_response(response: dict, threshold: float = 0.75):
    """Validate an agent response by its confidence score.

    Parameters
    ----------
    response:
        Dictionary expected to contain a ``confidence`` value.
    threshold:
        Minimum allowed confidence for a response to be considered valid.

    Returns
    -------
    dict
        ``{"valid": True, "response": response}`` if the response meets the
        threshold, otherwise ``{"valid": False, "reason": str}``.
    """
    confidence = response.get("confidence", 0)

    # If the confidence score does not meet the threshold we emit a warning
    # and notify the agent-feed for observability purposes.
    if confidence < threshold:
        logger.warning(
            "Hallucination guard triggered", extra={"confidence": confidence, "threshold": threshold}
        )
        post_agent_feed(f"Hallucination detected: {confidence:.2f}")
        return {"valid": False, "reason": "Low confidence (possible hallucination)"}

    logger.info(
        "Hallucination guard passed", extra={"confidence": confidence, "threshold": threshold}
    )

    # Pass the original response through so downstream middleware can continue
    return {"valid": True, "response": response}
