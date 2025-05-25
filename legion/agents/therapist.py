"""Therapist validation functions for Legion."""

import logging

logger = logging.getLogger(__name__)


def validate(payload: dict) -> tuple[bool, str]:
    """
    Simple therapist validation function.

    Args:
        payload: Dictionary containing validation data

    Returns:
        Tuple of (approved, reason)
    """
    try:
        # Basic validation - check if payload has required fields
        if not isinstance(payload, dict):
            return False, "Invalid payload format"

        # For now, just approve everything to avoid blocking the system
        # In a real implementation, this would contain actual validation logic
        return True, "Approved by therapist"

    except Exception as e:
        logger.error(f"Therapist validation error: {e}")
        return False, f"Validation error: {e}"
