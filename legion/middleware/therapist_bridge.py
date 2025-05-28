class RetryTrigger(Exception):
    """Raised when the therapist indicates a retry is required."""


def should_retry_from_therapist(response: dict) -> bool:
    """Check therapist response for retry signals."""
    message = str(response.get("detail") or response.get("message") or "").lower()
    for phrase in ("route blocked", "incomplete", "retry required"):
        if phrase in message:
            return True
    return False
