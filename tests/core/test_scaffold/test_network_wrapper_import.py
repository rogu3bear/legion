import unittest

class TestNetworkWrapperImport(unittest.TestCase):
    def test_import(self):
        from core.utils import network
        self.assertTrue(network)

if __name__ == '__main__':
    unittest.main()
