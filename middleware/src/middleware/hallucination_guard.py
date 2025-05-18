"""Simple hallucination guard based on confidence threshold."""

import logging

from legion.utils.agent_feed import post_agent_feed

logger = logging.getLogger(__name__)

import os


class HallucinationGuard:
    def __init__(self, threshold: float = None):
        self.threshold = float(
            threshold or os.getenv("HALLUCINATION_CONFIDENCE_THRESHOLD", 0.7)
        )

    def filter(self, response: dict) -> dict:
        """Add warning if confidence is below the configured threshold."""
        confidence = response.get("confidence", 1.0)
        if confidence < self.threshold:
            response["warning"] = "low_confidence"
            logger.warning(
                "Low confidence response", extra={"confidence": confidence, "threshold": self.threshold}
            )
            post_agent_feed(f"Response confidence {confidence:.2f} below threshold")
        else:
            logger.debug(
                "Response confidence acceptable", extra={"confidence": confidence}
            )
        return response
