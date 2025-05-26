"""Network utilities for Legion."""

import logging
import os
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)


def placeholder_network(url: Optional[str] = None, timeout: float = 2.0) -> dict:
    """
    Perform a basic HTTP GET health check and return status and response time.
    """
    if url is None:
        # Use environment variable or default port
        port = os.getenv("WEB_API_PORT", "27001")
        url = f"http://localhost:{port}/"

    try:
        start = time.time()
        resp = requests.get(url, timeout=timeout)
        elapsed = time.time() - start
        return {
            "ok": resp.status_code == 200,
            "status": resp.status_code,
            "elapsed": elapsed,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def health_check(url: str, timeout: float = 2.0) -> bool:
    """HTTP GET, return True if 200 else False."""
    logger.info("Performing health check", extra={"url": url, "timeout": timeout})
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            logger.info(
                "Health check successful",
                extra={"url": url, "status_code": resp.status_code},
            )
            return True
        else:
            logger.warning(
                "Health check failed",
                extra={"url": url, "status_code": resp.status_code},
            )
            return False
    except requests.exceptions.RequestException as e:
        logger.error("Health check error", extra={"url": url, "error": str(e)})
        return False
