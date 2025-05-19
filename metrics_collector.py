"""Background metrics collection job."""

import asyncio
import os

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    redis = None

from legion.agents.python.metrics import MetricsAgent


class MetricsCollector:
    """Periodically collect metrics using MetricsAgent."""

    def __init__(self) -> None:
        self.agent = MetricsAgent(name="metrics", config={})
        self.lock_key = "metrics:lock"
        self.client = self._get_redis()

    def _get_redis(self):
        if redis is None:
            return None
        try:
            port = int(os.getenv("REDIS_PORT", 7810))
            return redis.Redis(host="localhost", port=port, decode_responses=True)
        except Exception:
            return None

    async def start(self) -> None:
        """Run the collector loop."""
        while True:
            if self.client is not None:
                acquired = self.client.set(self.lock_key, "1", ex=10, nx=True)
            else:
                acquired = True
            if acquired:
                await self.agent.collect_stats()
            await asyncio.sleep(15)


def main() -> None:
    collector = MetricsCollector()
    asyncio.run(collector.start())


if __name__ == "__main__":
    main()
