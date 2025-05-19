import unittest
import importlib.util
import sys
import types

# Stub minimal package tree so doctor module can load without dependencies
legion_pkg = types.ModuleType("legion")
agents_pkg = types.ModuleType("legion.agents")
python_pkg = types.ModuleType("legion.agents.python")
base_pkg = types.ModuleType("legion.agents.base")
class BaseAgent:
    def __init__(self, *args, **kwargs):
        pass
base_pkg.BaseAgent = BaseAgent
sys.modules.update({
    "legion": legion_pkg,
    "legion.agents": agents_pkg,
    "legion.agents.python": python_pkg,
    "legion.agents.base": base_pkg,
    "yaml": types.ModuleType("yaml"),
    "numpy": types.ModuleType("numpy"),
    "openai": types.ModuleType("openai"),
    "dotenv": types.ModuleType("dotenv"),
    "discord": types.ModuleType("discord"),
    "zmq.asyncio": types.ModuleType("zmq.asyncio"),
})

spec = importlib.util.spec_from_file_location("doctor", "legion/agents/python/doctor.py")
doctor_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doctor_mod)  # type: ignore
DoctorAgent = doctor_mod.DoctorAgent


class TestDoctorAgent(unittest.TestCase):
    def setUp(self):
        self.agent = DoctorAgent("doctor", {})
        self.agent.redis = None  # disable redis during tests

    def test_symptom_to_diagnosis(self):
        symptoms = {"error": "cpu_high"}
        diag = self.agent.diagnose_issue(symptoms)
        self.assertEqual(diag["issue"], "High CPU Usage")
        self.assertEqual(diag["severity"], "critical")

    def test_diagnosis_to_remedy(self):
        diagnosis = {"issue": "Memory Leak"}
        remedies = self.agent.suggest_remedy(diagnosis)
        self.assertIn("Restart process", remedies)


if __name__ == "__main__":
    unittest.main()
