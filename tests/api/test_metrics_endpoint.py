import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from interface.main import app


class MetricsEndpointTests(unittest.TestCase):
    """Tests for the /metrics endpoint."""

    def setUp(self):
        self.client = TestClient(app)

    @patch("interface.api.v1.endpoints.metrics.get_redis_client")
    def test_metrics_endpoint_basic(self, mock_client):
        fake = MagicMock()
        fake.hgetall.return_value = {
            "legion_tasks_total": "5",
            "legion_agents_registered": "2",
        }
        mock_client.return_value = fake
        resp = self.client.get("/api/v1/metrics")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("legion_tasks_total", resp.text)


if __name__ == "__main__":
    unittest.main()
