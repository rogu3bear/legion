"""HTTP client wrapper for agent-to-middleware routing."""

import os
import time
from typing import Optional

import requests


class HTTPClient:
    def __init__(
        self,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        timeout: float = 10,
    ):
        self.base_url = os.getenv("MIDDLEWARE_URL")
        if not self.base_url:
            raise ValueError("MIDDLEWARE_URL env var is not set")
        self.max_retries = int(max_retries or os.getenv("HTTP_CLIENT_MAX_RETRIES", 3))
        self.backoff_factor = float(
            backoff_factor or os.getenv("HTTP_CLIENT_BACKOFF", 2)
        )
        self.timeout = timeout
        self.session = requests.Session()

    def post(
        self, path: str, json: Optional[dict] = None, headers: Optional[dict] = None
    ) -> dict:
        url = self.base_url.rstrip("/") + path
        hdrs = headers.copy() if headers else {}
        hdrs["X-Agent-Name"] = os.getenv("AGENT_NAME", "unknown")
        for attempt in range(self.max_retries):
            try:
                resp = self.session.post(
                    url, json=json, headers=hdrs, timeout=self.timeout
                )
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.backoff_factor * (2**attempt))

    def get(self, path: str, headers: Optional[dict] = None) -> dict:
        url = self.base_url.rstrip("/") + path
        hdrs = headers.copy() if headers else {}
        hdrs["X-Agent-Name"] = os.getenv("AGENT_NAME", "unknown")
        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(url, headers=hdrs, timeout=self.timeout)
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.backoff_factor * (2**attempt))
