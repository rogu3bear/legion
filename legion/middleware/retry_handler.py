import asyncio
import hashlib
import logging
from typing import Any, Awaitable, Callable

import httpx

from .log_utils import write_echo_log

logger = logging.getLogger(__name__)


async def retry_prompt(
    agent_call: Callable[[], Awaitable[Any]],
    max_retries: int = 2,
    delay: int = 2,
) -> Any:
    """Execute ``agent_call`` with retry logic.

    Retries on ``TimeoutError``, HTTP 5xx errors, ``ValueError`` or ``None``
    responses using exponential backoff.
    """
    trace_id = hashlib.sha256(str(asyncio.get_event_loop().time()).encode()).hexdigest()
    attempt = 1
    while True:
        try:
            result = await agent_call()
            if result is None:
                raise ValueError("None response")
            return result
        except Exception as exc:  # noqa: BLE001
            retry = False
            if isinstance(exc, TimeoutError):
                retry = True
            elif isinstance(exc, httpx.HTTPStatusError) and 500 <= exc.response.status_code < 600:
                retry = True
            elif isinstance(exc, ValueError):
                retry = True
            if not retry or attempt > max_retries:
                logger.error("retry_prompt aborting after %d attempts", attempt, exc_info=exc)
                raise
            write_echo_log(
                "Retry",
                trace_id=trace_id,
                attempt=attempt + 1,
                error=exc.__class__.__name__,
            )
            await asyncio.sleep(delay * (2 ** (attempt - 1)))
            attempt += 1
