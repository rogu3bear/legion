import unittest

class TestIndexingWrapperImport(unittest.TestCase):
    def test_import(self):
        from core.utils import indexing
        self.assertTrue(indexing)

if __name__ == '__main__':
    unittest.main()
