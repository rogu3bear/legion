"""Hallucination guard for agent responses."""


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
        return {"valid": False, "reason": "Low confidence (possible hallucination)"}
    return {"valid": True, "response": response}
