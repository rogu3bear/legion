"""Network utilities for Legion."""

import requests


def placeholder_network():
    pass


def health_check(url: str, timeout: float = 2.0) -> bool:
    """HTTP GET, return True if 200 else False."""
    try:
        resp = requests.get(url, timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False
