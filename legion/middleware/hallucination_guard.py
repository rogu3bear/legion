"""Hallucination guard for agent responses."""

import logging

from legion.utils.agent_feed import post_agent_feed

logger = logging.getLogger(__name__)


def guard_response(response: dict, threshold: float = 0.75):
    """
    Checks the confidence score of a response and flags potential hallucinations.

    Args:
        response: The response dictionary, expected to have a 'confidence' key.
        threshold: The minimum confidence score to be considered valid.

    Returns:
        A dictionary indicating if the response is valid and the reason if not.
    """
    confidence = response.get("confidence", 0)
    if confidence < threshold:
        logger.warning(
            "Hallucination guard triggered", extra={"confidence": confidence, "threshold": threshold}
        )
        post_agent_feed(f"Hallucination detected: {confidence:.2f}")
        return {"valid": False, "reason": "Low confidence (possible hallucination)"}

    logger.info(
        "Hallucination guard passed", extra={"confidence": confidence, "threshold": threshold}
    )
    return {"valid": True, "response": response}
