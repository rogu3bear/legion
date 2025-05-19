import os
import sqlite3
import tempfile
import unittest
import asyncio
import importlib.util
import sys
import types
sys.modules.setdefault("openai", types.ModuleType("openai"))
sys.modules.setdefault("legion.core.di_container", types.ModuleType("di_container"))
sys.modules.setdefault("legion.core.logging_config", types.ModuleType("logging_config"))
sys.modules.setdefault("legion.core.prompt_builder", types.ModuleType("prompt_builder"))

DB_UTILS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "legion", "core", "db_utils.py")
DOCTOR_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "legion", "agents", "python", "doctor.py")
METRICS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "legion", "agents", "python", "metrics.py")
BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "legion", "agents", "base.py")
MEMORY_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "memory", "legion_memory.py")

def load_module(path, fqname):
    parts = fqname.split(".")
    for i in range(1, len(parts)):
        pkg = ".".join(parts[:i])
        if pkg not in sys.modules:
            mod = types.ModuleType(pkg)
            mod.__path__ = []
            sys.modules[pkg] = mod
    spec = importlib.util.spec_from_file_location(fqname, os.path.abspath(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[fqname] = module
    spec.loader.exec_module(module)
    return module

db_utils = load_module(DB_UTILS_PATH, "legion.core.db_utils")
# Stub BaseAgent to avoid heavy dependencies
base_mod = types.ModuleType("legion.agents.base")
class BaseAgent:
    def __init__(self, name: str, config: dict, llm_client=None):
        self.name = name
        self.config = config
        self.llm_client = llm_client
base_mod.BaseAgent = BaseAgent
sys.modules["legion.agents.base"] = base_mod
load_module(MEMORY_PATH, "memory.legion_memory")
doctor_mod = load_module(DOCTOR_PATH, "legion.agents.python.doctor")
metrics_mod = load_module(METRICS_PATH, "legion.agents.python.metrics")
DoctorAgent = doctor_mod.DoctorAgent
MetricsAgent = metrics_mod.MetricsAgent


class TestDBUtils(unittest.TestCase):
    def test_init_db_creates_table(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            db_utils.init_db(db_path)
            conn = sqlite3.connect(db_path)
            try:
                cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='example'")
                self.assertIsNotNone(cur.fetchone())
            finally:
                conn.close()


class TestAgents(unittest.TestCase):
    def test_doctor_assessment(self):
        agent = DoctorAgent(name="doctor", config={})
        result = asyncio.run(agent.assess_patient("patient has fever"))
        self.assertIn("febrile", result.lower())

    def test_metrics_collect(self):
        agent = MetricsAgent(name="metrics", config={})
        metrics = asyncio.run(agent.collect_metrics())
        self.assertIn("pid", metrics)


if __name__ == "__main__":
    unittest.main()
