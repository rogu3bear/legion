import asyncio
import json
import time
import unittest

from legion.agents.metrics.metrics_agent import MetricsAgent
from tests.stubs.fakeredis_stub import StrictRedis


class FakeRedis(StrictRedis):
    def __init__(self):
        super().__init__()
        self._sets = {}
        self._strings = {}

    def smembers(self, name):
        return self._sets.get(name, set())

    def sadd(self, name, member):
        self._sets.setdefault(name, set()).add(member)

    def set(self, key, value):
        self._strings[key] = value

    def get(self, key):
        return self._strings.get(key)

    def zcard(self, name):
        return len(self._zsets.get(name, {}))


class MetricsAgentTests(unittest.TestCase):
    def test_collect_updates_payload(self):
        r = FakeRedis()
        r.zadd("queue:tasks", {"t1": 1})
        r.sadd("agents:set", "a1")
        r.hset("agents:a1", "heartbeat_ts", str(int(time.time()) - 5))
        agent = MetricsAgent(r)

        asyncio.get_event_loop().run_until_complete(agent.collect())

        raw = r.get(MetricsAgent.KEY)
        self.assertIsNotNone(raw)
        data = json.loads(raw)
        self.assertIn("queue_depth", data)
        self.assertIn("agent_heartbeat_age", data)


if __name__ == "__main__":
    unittest.main()
