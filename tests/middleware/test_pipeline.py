import tempfile
import types
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Provide a minimal YAML stub so imports succeed without PyYAML
if 'yaml' not in sys.modules:
    yaml_stub = types.ModuleType('yaml')
    yaml_stub.safe_load = lambda *_args, **_kwargs: {}
    yaml_stub.YAMLError = Exception
    yaml_stub.dump = lambda *args, **kwargs: ""
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

from legion.middleware import run_middleware_pipeline, validator


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directives = {"agent": {"allowed_directives": ["ok"]}}
        self.load_patch = patch.object(validator, "_load_directives_config", return_value=self.directives)
        self.load_patch.start()
        validator._loaded_directives = None
        self.dir_patch = patch.object(validator, "DIRECTIVES_PATH", str(Path(self.temp_dir.name) / "directives.yaml"))
        self.dir_patch.start()
        self.feed_patch = patch("legion.middleware.post_agent_feed")
        self.feed_patch.start()

    def tearDown(self):
        self.feed_patch.stop()
        self.dir_patch.stop()
        self.load_patch.stop()
        self.temp_dir.cleanup()

    def test_pipeline_success(self):
        with patch("legion.middleware.therapist_validate", return_value={"valid": True, "directive": "ok"}):
            result = run_middleware_pipeline(
                {"agent": "agent", "directive": "ok", "confidence": 0.9}, confidence_threshold=0.75
            )
            self.assertTrue(result["final_valid"])
            self.assertEqual(result["source"], "all_middleware_approved")

    def test_pipeline_invalid_directive(self):
        with patch("legion.middleware.therapist_validate", return_value={"valid": True, "directive": "ok"}):
            result = run_middleware_pipeline(
                {"agent": "agent", "directive": "bad", "confidence": 0.9}, confidence_threshold=0.75
            )
            self.assertFalse(result["final_valid"])
            self.assertEqual(result["source"], "validator")

    def test_pipeline_low_confidence(self):
        with patch("legion.middleware.therapist_validate", return_value={"valid": False, "reason": "low"}):
            result = run_middleware_pipeline(
                {"agent": "agent", "directive": "ok", "confidence": 0.5}, confidence_threshold=0.75
            )
            self.assertFalse(result["final_valid"])
            self.assertEqual(result["source"], "therapist")


if __name__ == "__main__":
    unittest.main()
