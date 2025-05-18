import unittest
from unittest.mock import patch
from types import ModuleType
import sys

try:
    import yaml  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover - dependency not installed
    yaml = ModuleType("yaml")
    import json
    yaml.safe_dump = lambda data, fh, *a, **k: json.dump(data, fh)
    yaml.safe_load = lambda s, *a, **k: json.load(s)
    sys.modules["yaml"] = yaml

if "legion.orchestrator" not in sys.modules:
    stub = ModuleType("legion.orchestrator")
    class DummyOrchestrator:
        def run_once(self):
            return []
    stub.Orchestrator = DummyOrchestrator
    sys.modules["legion.orchestrator"] = stub

from legion.middleware.hallucination_guard import guard_response


class TestHallucinationGuard(unittest.TestCase):
    """Tests for the :func:`guard_response` helper."""

    def test_guard_response_valid(self):
        with patch("legion.middleware.hallucination_guard.post_agent_feed") as mock_post:
            result = guard_response({"confidence": 0.9}, threshold=0.8)
            self.assertTrue(result["valid"])
            self.assertEqual(result["response"]["confidence"], 0.9)
            mock_post.assert_not_called()

    def test_guard_response_invalid(self):
        with patch("legion.middleware.hallucination_guard.post_agent_feed") as mock_post:
            result = guard_response({"confidence": 0.5}, threshold=0.8)
            self.assertFalse(result["valid"])
            self.assertIn("Low confidence", result["reason"])
            mock_post.assert_called_once()

    def test_guard_response_no_confidence(self):
        with patch("legion.middleware.hallucination_guard.post_agent_feed") as mock_post:
            result = guard_response({}, threshold=0.8)
            self.assertFalse(result["valid"])
            mock_post.assert_called_once()


if __name__ == "__main__":
    unittest.main()
