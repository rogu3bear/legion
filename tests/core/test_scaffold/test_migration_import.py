import unittest

class TestMigrationImport(unittest.TestCase):
    def test_import(self):
        from core.db.migrations import _
        self.assertTrue(_)

if __name__ == '__main__':
    unittest.main()
