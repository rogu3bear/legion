import types
import sys
import unittest
from unittest.mock import patch

# Provide a minimal YAML stub so imports succeed without PyYAML
if 'yaml' not in sys.modules:
    yaml_stub = types.ModuleType('yaml')
    yaml_stub.safe_load = lambda *_args, **_kwargs: {}
    yaml_stub.YAMLError = Exception
    sys.modules['yaml'] = yaml_stub
if 'zmq' not in sys.modules:
    zmq_stub = types.ModuleType('zmq')
    zmq_asyncio = types.ModuleType('zmq.asyncio')
    zmq_stub.asyncio = zmq_asyncio
    sys.modules['zmq'] = zmq_stub
    sys.modules['zmq.asyncio'] = zmq_asyncio
if 'dotenv' not in sys.modules:
    dotenv_stub = types.ModuleType('dotenv')
    dotenv_stub.dotenv_values = lambda *_args, **_kwargs: {}
    sys.modules['dotenv'] = dotenv_stub
if 'legion.orchestrator' not in sys.modules:
    orchestrator_stub = types.ModuleType('legion.orchestrator')
    class Orchestrator:
        pass
    orchestrator_stub.Orchestrator = Orchestrator
    sys.modules['legion.orchestrator'] = orchestrator_stub

from legion.middleware.hallucination_guard import guard_response


class HallucinationGuardTests(unittest.TestCase):
    def test_guard_response_valid(self):
        with patch("legion.middleware.hallucination_guard.post_agent_feed") as post:
            result = guard_response({"confidence": 0.9}, threshold=0.8)
            self.assertTrue(result["valid"])
            self.assertEqual(result["response"]["confidence"], 0.9)
            post.assert_not_called()

    def test_guard_response_invalid(self):
        with patch("legion.middleware.hallucination_guard.post_agent_feed") as post:
            result = guard_response({"confidence": 0.5}, threshold=0.8)
            self.assertFalse(result["valid"])
            self.assertIn("Low confidence", result["reason"])
            post.assert_called_once()

    def test_guard_response_no_confidence(self):
        with patch("legion.middleware.hallucination_guard.post_agent_feed") as post:
            result = guard_response({}, threshold=0.8)
            self.assertFalse(result["valid"])
            post.assert_called_once()


if __name__ == "__main__":
    unittest.main()
