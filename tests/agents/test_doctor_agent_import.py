import unittest

class TestDoctorAgentImport(unittest.TestCase):
    def test_import(self):
        import importlib.util
        import sys
        import types

        # Stub minimal package structure to satisfy imports
        legion_pkg = types.ModuleType("legion")
        agents_pkg = types.ModuleType("legion.agents")
        python_pkg = types.ModuleType("legion.agents.python")
        base_pkg = types.ModuleType("legion.agents.base")
        class BaseAgent:
            def __init__(self, *args, **kwargs):
                pass
        base_pkg.BaseAgent = BaseAgent
        sys.modules.update({
            "legion": legion_pkg
            "legion.agents": agents_pkg
            "legion.agents.python": python_pkg
            "legion.agents.base": base_pkg
            "yaml": types.ModuleType("yaml")
            "numpy": types.ModuleType("numpy")
            "openai": types.ModuleType("openai")
            "dotenv": types.ModuleType("dotenv")
            "discord": types.ModuleType("discord")
            "zmq.asyncio": types.ModuleType("zmq.asyncio")
        })

        spec = importlib.util.spec_from_file_location("doctor", "legion/agents/python/doctor.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
        self.assertTrue(hasattr(module, "DoctorAgent"))

if __name__ == '__main__':
    unittest.main()
