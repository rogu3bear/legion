import unittest
import sys
import types

# Provide minimal stubs for optional dependencies
yaml_stub = types.ModuleType("yaml")
yaml_stub.dump = lambda data, f, **kw: __import__('json').dump(data, f)
yaml_stub.safe_load = lambda f: __import__('json').load(f)
sys.modules.setdefault("yaml", yaml_stub)
orch_stub = types.ModuleType("legion.orchestrator")
class _DummyOrchestrator: ...
orch_stub.Orchestrator = _DummyOrchestrator
sys.modules.setdefault("legion.orchestrator", orch_stub)

from middleware.src.middleware.directive_compliance import DirectiveCompliance


class TestDirectiveCompliance(unittest.TestCase):
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
