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

from legion.middleware import validator


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directives = {"exec": {"allowed_directives": ["run"]}}
        self.load_patch = patch.object(validator, "_load_directives_config", return_value=self.directives)
        self.load_patch.start()
        validator._loaded_directives = None

    def tearDown(self):
        self.load_patch.stop()
        self.temp_dir.cleanup()

    def patch_config(self, path=None):
        if path is None:
            path = Path(self.temp_dir.name) / "directives.yaml"
        return patch.object(validator, "DIRECTIVES_PATH", str(path))

    def test_validate_directive_success(self):
        with self.patch_config():
            validator._loaded_directives = None
            result = validator.validate_directive({"agent": "exec", "directive": "run"})
            self.assertTrue(result["is_valid"])

    def test_validate_directive_invalid(self):
        with self.patch_config():
            validator._loaded_directives = None
            result = validator.validate_directive({"agent": "exec", "directive": "stop"})
            self.assertFalse(result["is_valid"])
            self.assertIn("not allowed", result["reason"])

    def test_validate_directive_missing_file(self):
        missing = Path(self.temp_dir.name) / "missing.yaml"
        with self.patch_config(missing), patch.object(validator, "_load_directives_config", return_value={}):
            validator._loaded_directives = None
            result = validator.validate_directive({"agent": "exec", "directive": "run"})
            self.assertFalse(result["is_valid"])
            self.assertIn("not allowed", result["reason"])

    def test_validate_directive_missing_keys(self):
        with self.patch_config():
            validator._loaded_directives = None
            result = validator.validate_directive({"directive": "run"})
            self.assertFalse(result["is_valid"])
            self.assertIn("Missing", result["reason"])


if __name__ == "__main__":
    unittest.main()
