import tempfile
import unittest
from pathlib import Path
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

from legion.middleware import validator


class TestValidator(unittest.TestCase):
    """Tests for directive validation logic."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)

    def _write_directives(self, data) -> Path:
        path = Path(self.tmpdir.name) / "directives.yaml"
        with open(path, "w") as fh:
            yaml.safe_dump(data, fh)
        return path

    def test_validate_directive_success(self):
        path = self._write_directives({"exec": {"allowed_directives": ["run"]}})
        with patch.object(validator, "DIRECTIVES_PATH", str(path)):
            validator._loaded_directives = None
            result = validator.validate_directive({"agent": "exec", "directive": "run"})
            self.assertTrue(result["is_valid"])

    def test_validate_directive_invalid(self):
        path = self._write_directives({"exec": {"allowed_directives": ["run"]}})
        with patch.object(validator, "DIRECTIVES_PATH", str(path)):
            validator._loaded_directives = None
            result = validator.validate_directive({"agent": "exec", "directive": "stop"})
            self.assertFalse(result["is_valid"])
            self.assertIn("not allowed", result["reason"])

    def test_validate_directive_missing_file(self):
        missing = Path(self.tmpdir.name) / "missing.yaml"
        with patch.object(validator, "DIRECTIVES_PATH", str(missing)):
            validator._loaded_directives = None
            result = validator.validate_directive({"agent": "exec", "directive": "run"})
            self.assertFalse(result["is_valid"])
            self.assertIn("not allowed", result["reason"])

    def test_validate_directive_missing_keys(self):
        path = self._write_directives({"exec": {"allowed_directives": ["run"]}})
        with patch.object(validator, "DIRECTIVES_PATH", str(path)):
            validator._loaded_directives = None
            result = validator.validate_directive({"directive": "run"})
            self.assertFalse(result["is_valid"])
            self.assertIn("Missing", result["reason"])


if __name__ == "__main__":
    unittest.main()
