import unittest
import importlib.util
import sys
import types
from unittest.mock import patch

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

spec = importlib.util.spec_from_file_location("researcher", "legion/agents/python/researcher.py")
researcher_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(researcher_mod)  # type: ignore
ResearcherAgent = researcher_mod.ResearcherAgent


class TestResearcherAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ResearcherAgent("researcher", {})
        self.agent.redis = None

    @patch.object(researcher_mod, "search_web")
    @patch.object(researcher_mod, "summarize_texts")
    def test_research_flow(self, mock_summary, mock_search):
        mock_search.return_value = ["data1", "data2"]
        mock_summary.return_value = "x" * 210

        raw = self.agent.conduct_research("test", ["src"])
        self.assertEqual(raw, ["data1", "data2"])

        report = self.agent.synthesize_findings(raw)
        self.assertEqual(report, "x" * 210)
        self.assertGreaterEqual(len(report), 200)


if __name__ == "__main__":
    unittest.main()
