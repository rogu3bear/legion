import unittest

class TestCoreInitImport(unittest.TestCase):
    def test_import(self):
        import core
        self.assertTrue(core)

if __name__ == '__main__':
    unittest.main()
