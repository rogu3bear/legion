import unittest

class TestDoctorAgentImport(unittest.TestCase):
    def test_import(self):
        from legion.agents.python.doctor import DoctorAgent
        self.assertTrue(DoctorAgent)

if __name__ == '__main__':
    unittest.main()
