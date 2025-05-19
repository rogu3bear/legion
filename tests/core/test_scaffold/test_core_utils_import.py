import unittest

class TestCoreUtilsImport(unittest.TestCase):
    def test_import(self):
        from core.utils import network, indexing
        self.assertTrue(network)
        self.assertTrue(indexing)

if __name__ == '__main__':
    unittest.main()
