import asyncio
from typing import Callable, Iterable, Type

async def async_retry(func: Callable, retries: int = 3, delay: float = 1.0,
                      exceptions: Iterable[Type[BaseException]] = (Exception,)):
    for attempt in range(retries):
        try:
            return await func()
        except exceptions as exc:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(delay * (2 ** attempt))
