import unittest


def mark_legacy(testcase):
    return unittest.skip("legacy failure – deferred")(testcase)
