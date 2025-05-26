import sys
import unittest
from unittest.mock import patch

from tests.middleware.orchestrator_stub import orchestrator_stub

sys.modules.setdefault('legion.orchestrator', orchestrator_stub)

from middleware.src.middleware.directive_compliance import DirectiveCompliance


class DirectiveComplianceTests(unittest.TestCase):
    def setUp(self):
        self.patch_feed = patch('middleware.src.middleware.directive_compliance.post_agent_feed')
        self.mock_feed = self.patch_feed.start()
        self.dc = DirectiveCompliance()

    def tearDown(self):
        self.patch_feed.stop()

    def test_length_violation(self):
        long_text = 'x' * 2000
        status, details = self.dc.check(long_text, {'task_id': '1'})
        self.assertEqual(status, 'non_compliant')
        self.assertIn('max_length_exceeded', details.get('breach_type', ''))

    def test_prohibited_keyword_triggers_therapist(self):
        text = 'please sudo rm -rf /'
        status, details = self.dc.check(text, {'task_id': '1'})
        self.assertEqual(status, 'non_compliant')
        self.assertIn('prohibited_keyword', details.get('breach_type', ''))

    def test_missing_required_field(self):
        status, details = self.dc.check('ok', {})
        self.assertEqual(status, 'non_compliant')
        self.assertIn('missing_metadata', details.get('breach_type', ''))

    def test_compliant_request(self):
        status, details = self.dc.check('summarize', {'task_id': '1'}, agent_id='researcher_agent')
        self.assertEqual(status, 'compliant')
        self.assertEqual(details['checks_failed'], [])


if __name__ == '__main__':
    unittest.main()
