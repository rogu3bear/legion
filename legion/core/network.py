"""Network utilities for Legion."""

import time
import logging

import requests

logger = logging.getLogger(__name__)


def placeholder_network(
    url: str = "http://localhost:8000/", timeout: float = 2.0
) -> dict:
    """
    Perform a basic HTTP GET health check and return status and response time.
    """
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
            logger.info("Health check successful", extra={"url": url, "status_code": resp.status_code})
            return True
        else:
            logger.warning("Health check failed", extra={"url": url, "status_code": resp.status_code})
            return False
    except requests.exceptions.RequestException as e:
        logger.error("Health check error", extra={"url": url, "error": str(e)})
        return False


def fetch_with_retries(url, retries=3, timeout=2.0, backoff=0.5):
    """HTTP GET with retry logic. Returns response or raises last error."""
    logger.info("Fetching with retries", extra={"url": url, "retries": retries, "timeout": timeout, "backoff": backoff})
    last_error = None
    for attempt in range(retries):
        try:
            start_time = time.time()
            resp = requests.get(url, timeout=timeout)
            elapsed = time.time() - start_time
            if resp.status_code == 200:
                logger.info("Fetch successful", extra={"url": url, "status_code": resp.status_code, "elapsed_time": elapsed, "attempt": attempt + 1})
                return resp
            else:
                logger.warning("Fetch failed", extra={"url": url, "status_code": resp.status_code, "elapsed_time": elapsed, "attempt": attempt + 1})
                last_error = Exception(f"Status code: {resp.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error("Fetch error", extra={"url": url, "error": str(e), "attempt": attempt + 1})
            last_error = e
        if attempt < retries - 1:
            logger.info("Retrying after backoff", extra={"url": url, "attempt": attempt + 1, "backoff": backoff})
            time.sleep(backoff)
    logger.error("All retries failed", extra={"url": url, "retries": retries, "last_error": str(last_error)})
    raise last_error
