import types
import sys
import unittest

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

from middleware.src.middleware.directive_compliance import DirectiveCompliance


class DirectiveComplianceTests(unittest.TestCase):
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
