import unittest

class TestCoreDBImport(unittest.TestCase):
    def test_import(self):
        import core.db
        self.assertTrue(core.db)

if __name__ == '__main__':
    unittest.main()
