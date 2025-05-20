import json
import unittest

from fastapi import FastAPI

import interface.api.v1.endpoints.metrics as metrics_ep
from tests.stubs.fakeredis_stub import StrictRedis
from tests.stubs.testclient import TestClient


class FakeRedis(StrictRedis):
    def __init__(self):
        super().__init__()
        self._strings = {}

    def set(self, key, value):
        self._strings[key] = value

    def get(self, key):
        return self._strings.get(key)


class MetricsSummaryTests(unittest.TestCase):
    def setUp(self):
        self.redis = FakeRedis()
        metrics_ep.get_redis_client = lambda: self.redis
        app = FastAPI()
        app.include_router(metrics_ep.router, prefix="/api/v1/metrics")
        self.client = TestClient(app)

    def test_summary_endpoint(self):
        payload = {"queue_depth": 3}
        self.redis.set("metrics:latest", json.dumps(payload))
        resp = self.client.get("/api/v1/metrics/summary")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["queue_depth"], 3)


if __name__ == "__main__":
    unittest.main()
