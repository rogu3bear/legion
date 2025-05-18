import sys
import unittest
from unittest.mock import patch

from tests.middleware.orchestrator_stub import orchestrator_stub

sys.modules.setdefault('legion.orchestrator', orchestrator_stub)

from legion.middleware.hallucination_guard import guard_response


class HallucinationGuardTests(unittest.TestCase):
    def test_guard_response_valid(self):
        with patch('legion.middleware.hallucination_guard.post_agent_feed') as mock_post:
            result = guard_response({'confidence': 0.9}, threshold=0.8)
            self.assertTrue(result['valid'])
            self.assertEqual(result['response']['confidence'], 0.9)
            mock_post.assert_not_called()

    def test_guard_response_invalid(self):
        with patch('legion.middleware.hallucination_guard.post_agent_feed') as mock_post:
            result = guard_response({'confidence': 0.5}, threshold=0.8)
            self.assertFalse(result['valid'])
            self.assertIn('Low confidence', result['reason'])
            mock_post.assert_called_once()

    def test_guard_response_no_confidence(self):
        with patch('legion.middleware.hallucination_guard.post_agent_feed') as mock_post:
            result = guard_response({}, threshold=0.8)
            self.assertFalse(result['valid'])
            mock_post.assert_called_once()


if __name__ == '__main__':
=======
import unittest

from legion.middleware import hallucination_guard


class TestHallucinationGuard(unittest.TestCase):
    """Scaffold tests for :func:`guard_response`."""

    def setUp(self):
        """Set up test fixtures."""
        pass

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test_valid_confidence(self):
        """Handle responses above the threshold."""
        pass

    def test_invalid_confidence(self):
        """Handle responses below the threshold."""
        pass

    def test_missing_confidence(self):
        """Handle responses without a confidence value."""
        pass


if __name__ == "__main__":
    unittest.main()
