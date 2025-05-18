"""Utilities for validating response confidence."""

import os
from typing import Dict


class HallucinationGuard:
    """Check confidence scores and flag potential hallucinations."""

    def __init__(self, threshold: float | None = None) -> None:
        self.threshold = float(
            threshold or os.getenv("HALLUCINATION_CONFIDENCE_THRESHOLD", 0.75)
        )

    def check(self, response: Dict) -> Dict:
        """Validate confidence against the configured threshold."""
        confidence = response.get("confidence", 0)
        if confidence < self.threshold:
            return {"valid": False, "reason": "Low confidence (possible hallucination)"}
        return {"valid": True, "response": response}

    @staticmethod
    def guard_response(response: Dict, threshold: float = 0.75) -> Dict:
        """Stateless helper for quick checks."""
        return HallucinationGuard(threshold).check(response)
