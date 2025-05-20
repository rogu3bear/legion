import asyncio
import os

from legion.agents.metrics.metrics_agent import MetricsAgent


async def main() -> None:
    agent = MetricsAgent()
    while True:
        await agent.collect()
        await asyncio.sleep(int(os.getenv("METRICS_INTERVAL", "60")))


if __name__ == "__main__":
    asyncio.run(main())
