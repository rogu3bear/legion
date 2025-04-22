"""Network utilities for Legion."""

import time
import requests
import logging

logger = logging.getLogger(__name__)

def fetch_with_retries(url: str, retries: int = 3, delay: int = 1) -> requests.Response:
    """Fetch URL with basic retry logic."""
    for i in range(retries):
        try:
            logger.debug(f"Attempt {i+1}/{retries} to fetch {url}")
            response = requests.get(url)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            logger.debug(f"Successfully fetched {url} on attempt {i+1}")
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {i+1}/{retries} failed for {url}: {e}")
            if i < retries - 1:
                logger.info(f"Retrying fetch for {url} in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to fetch {url} after {retries} attempts.")
                raise e
    # Should not be reached, but needed for type hinting
    raise RuntimeError("Exhausted retries without success") 