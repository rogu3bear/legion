import unittest

from tests.legacy_skip import mark_legacy


@mark_legacy
class LegacyPlaceHolder(unittest.TestCase):
    pass
