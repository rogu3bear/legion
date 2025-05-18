import unittest
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

from types import ModuleType
import sys

try:
    import yaml  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    yaml = ModuleType("yaml")
    yaml.safe_dump = lambda *a, **k: ""
    yaml.safe_load = lambda *a, **k: {}
    sys.modules["yaml"] = yaml

if "legion.orchestrator" not in sys.modules:
    stub = ModuleType("legion.orchestrator")
    class DummyOrchestrator:
        def run_once(self):
            return []
    stub.Orchestrator = DummyOrchestrator
    sys.modules["legion.orchestrator"] = stub

from middleware.src.middleware.directive_compliance import DirectiveCompliance


class TestDirectiveCompliance(unittest.TestCase):
    """Tests for directive compliance checks."""

    def setUp(self):
        self.dc = DirectiveCompliance()

    def test_length_violation(self):
        long_text = "x" * 2000
        status, details = self.dc.check(long_text, {"task_id": "1"})
        self.assertEqual(status, "non_compliant")
        self.assertIn("max_length_exceeded", details.get("breach_type", ""))

    def test_prohibited_keyword_triggers_therapist(self):
        text = "please sudo rm -rf /"
        status, details = self.dc.check(text, {"task_id": "1"})
        self.assertEqual(status, "non_compliant")
        self.assertIn("prohibited_keyword", details.get("breach_type", ""))

    def test_missing_required_field(self):
        status, details = self.dc.check("ok", {})
        self.assertEqual(status, "non_compliant")
        self.assertIn("missing_metadata", details.get("breach_type", ""))

    def test_compliant_request(self):
        status, details = self.dc.check("summarize", {"task_id": "1"}, agent_id="researcher_agent")
        self.assertEqual(status, "compliant")
        self.assertEqual(details["checks_failed"], [])


if __name__ == "__main__":
    unittest.main()
