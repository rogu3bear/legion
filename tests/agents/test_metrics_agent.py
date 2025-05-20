import asyncio
import unittest
from unittest.mock import MagicMock

from legion.agents.python.metrics import MetricsAgent


class MetricsAgentTests(unittest.TestCase):
    """Verify MetricsAgent redis updates."""

    def test_push_to_redis(self):
        agent = MetricsAgent(name="metrics", config={})
        fake = MagicMock()
        agent._redis = fake
        stats = {"task_queue_length": 3}
        asyncio.run(agent.push_to_redis(stats))
        fake.hset.assert_called_once_with("metrics:latest", mapping=stats)
        fake.incrby.assert_called_with("metrics_task_queue_length_total", 3)


@unittest.skip("legacy failure – deferred")
class LegacyPlaceHolder(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
