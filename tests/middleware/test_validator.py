import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys
import types

# Provide minimal stubs for optional dependencies
yaml_stub = types.ModuleType("yaml")
yaml_stub.dump = lambda data, f, **kw: __import__('json').dump(data, f)
yaml_stub.safe_load = lambda f: __import__('json').load(f)
sys.modules.setdefault("yaml", yaml_stub)
yaml = yaml_stub
orch_stub = types.ModuleType("legion.orchestrator")
class _DummyOrchestrator: ...
orch_stub.Orchestrator = _DummyOrchestrator
sys.modules.setdefault("legion.orchestrator", orch_stub)

from legion.middleware import validator


def setup_directives(tmp_dir: Path, data: dict) -> Path:
    path = tmp_dir / "directives.yaml"
    with open(path, "w") as fh:
        yaml.dump(data, fh)
    return path


class TestValidator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_validate_directive_success(self):
        tmp_path = Path(self.temp_dir.name)
        path = setup_directives(tmp_path, {"exec": {"allowed_directives": ["run"]}})
        with patch.object(validator, "DIRECTIVES_PATH", str(path)):
            validator._loaded_directives = None
            result = validator.validate_directive({"agent": "exec", "directive": "run"})
        self.assertTrue(result["is_valid"])

    def test_validate_directive_invalid(self):
        tmp_path = Path(self.temp_dir.name)
        path = setup_directives(tmp_path, {"exec": {"allowed_directives": ["run"]}})
        with patch.object(validator, "DIRECTIVES_PATH", str(path)):
            validator._loaded_directives = None
            result = validator.validate_directive({"agent": "exec", "directive": "stop"})
        self.assertFalse(result["is_valid"])
        self.assertIn("not allowed", result["reason"])

    def test_validate_directive_missing_file(self):
        tmp_path = Path(self.temp_dir.name)
        missing = tmp_path / "missing.yaml"
        with patch.object(validator, "DIRECTIVES_PATH", str(missing)):
            validator._loaded_directives = None
            result = validator.validate_directive({"agent": "exec", "directive": "run"})
        self.assertFalse(result["is_valid"])
        self.assertIn("not allowed", result["reason"])

    def test_validate_directive_missing_keys(self):
        tmp_path = Path(self.temp_dir.name)
        path = setup_directives(tmp_path, {"exec": {"allowed_directives": ["run"]}})
        with patch.object(validator, "DIRECTIVES_PATH", str(path)):
            validator._loaded_directives = None
            result = validator.validate_directive({"directive": "run"})
        self.assertFalse(result["is_valid"])
        self.assertIn("Missing", result["reason"])


if __name__ == "__main__":
    unittest.main()
