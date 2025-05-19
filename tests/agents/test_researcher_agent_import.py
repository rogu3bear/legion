import unittest

class TestResearcherAgentImport(unittest.TestCase):
    def test_import(self):
        from legion.agents.python.researcher import ResearcherAgent
        self.assertTrue(ResearcherAgent)

if __name__ == '__main__':
    unittest.main()
