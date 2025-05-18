import unittest
import sys
import types
from unittest.mock import patch

# Provide minimal stubs to satisfy package imports
yaml_stub = types.ModuleType("yaml")
yaml_stub.dump = lambda data, f, **kw: __import__('json').dump(data, f)
yaml_stub.safe_load = lambda f: __import__('json').load(f)
sys.modules.setdefault("yaml", yaml_stub)
orch_stub = types.ModuleType("legion.orchestrator")
class _DummyOrchestrator: ...
orch_stub.Orchestrator = _DummyOrchestrator
sys.modules.setdefault("legion.orchestrator", orch_stub)

from legion.middleware.hallucination_guard import guard_response


class TestHallucinationGuard(unittest.TestCase):
    @patch("legion.middleware.hallucination_guard.post_agent_feed")
    def test_guard_response_valid(self, mock_post):
        result = guard_response({"confidence": 0.9}, threshold=0.8)
        self.assertTrue(result["valid"])
        self.assertEqual(result["response"]["confidence"], 0.9)
        mock_post.assert_not_called()

    @patch("legion.middleware.hallucination_guard.post_agent_feed")
    def test_guard_response_invalid(self, mock_post):
        result = guard_response({"confidence": 0.5}, threshold=0.8)
        self.assertFalse(result["valid"])
        self.assertIn("Low confidence", result["reason"])
        mock_post.assert_called_once()

    @patch("legion.middleware.hallucination_guard.post_agent_feed")
    def test_guard_response_no_confidence(self, mock_post):
        result = guard_response({}, threshold=0.8)
        self.assertFalse(result["valid"])
        mock_post.assert_called_once()


if __name__ == "__main__":
    unittest.main()
