import unittest
from unittest.mock import patch
from types import ModuleType
import sys

try:
    import yaml  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
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

from legion.middleware import run_middleware_pipeline


class TestMiddlewarePipeline(unittest.TestCase):
    """Integration tests for the middleware pipeline."""

    def _run_pipeline(self, validator_result, guard_result, therapist_result, payload):
        with patch("legion.middleware.validate_directive", return_value=validator_result), \
             patch("legion.middleware.guard_response", return_value=guard_result), \
             patch("legion.middleware.therapist_validate", return_value=therapist_result), \
             patch("legion.middleware.post_agent_feed"):
            return run_middleware_pipeline(payload)

    def test_pipeline_success(self):
        result = self._run_pipeline(
            {"is_valid": True},
            {"valid": True, "response": {"confidence": 0.9}},
            {"valid": True, "directive": "ok"},
            {"agent": "a", "directive": "ok", "confidence": 0.9},
        )
        self.assertTrue(result["final_valid"])
        self.assertEqual(result["source"], "all_middleware_approved")

    def test_pipeline_invalid_directive(self):
        result = self._run_pipeline(
            {"is_valid": False, "reason": "bad"},
            {"valid": True, "response": {"confidence": 0.9}},
            {"valid": True},
            {"agent": "a", "directive": "bad", "confidence": 0.9},
        )
        self.assertFalse(result["final_valid"])
        self.assertEqual(result["source"], "validator")

    def test_pipeline_low_confidence(self):
        result = self._run_pipeline(
            {"is_valid": True},
            {"valid": False, "reason": "low"},
            {"valid": False, "reason": "low"},
            {"agent": "a", "directive": "ok", "confidence": 0.5},
        )
        self.assertFalse(result["final_valid"])
        self.assertEqual(result["source"], "therapist")


if __name__ == "__main__":
    unittest.main()
