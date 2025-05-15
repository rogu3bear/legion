"""Simple hallucination guard based on confidence threshold"""

import os


class HallucinationGuard:
    def __init__(self, threshold: float = None):
        self.threshold = float(
            threshold or os.getenv("HALLUCINATION_CONFIDENCE_THRESHOLD", 0.7)
        )

    def filter(self, response: dict) -> dict:
        """Add warning if confidence < threshold"""
        confidence = response.get("confidence", 1.0)
        if confidence < self.threshold:
            response["warning"] = "low_confidence"
        return response
