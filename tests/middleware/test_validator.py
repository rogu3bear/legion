import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests.middleware.yaml_stub import yaml
from tests.middleware.orchestrator_stub import orchestrator_stub
sys.modules['yaml'] = yaml
sys.modules.setdefault('legion.orchestrator', orchestrator_stub)
=======
import unittest

from legion.middleware import validator


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)

    def create_config(self, data):
        path = os.path.join(self.tmpdir.name, 'directives.yaml')
        with open(path, 'w') as fh:
            yaml.dump(data, fh)
        return path

    def test_validate_directive_success(self):
        path = self.create_config({'exec': {'allowed_directives': ['run']}})
        with patch.object(validator, 'DIRECTIVES_PATH', path):
            validator._loaded_directives = None
            result = validator.validate_directive({'agent': 'exec', 'directive': 'run'})
            self.assertTrue(result['is_valid'])

    def test_validate_directive_invalid(self):
        path = self.create_config({'exec': {'allowed_directives': ['run']}})
        with patch.object(validator, 'DIRECTIVES_PATH', path):
            validator._loaded_directives = None
            result = validator.validate_directive({'agent': 'exec', 'directive': 'stop'})
            self.assertFalse(result['is_valid'])
            self.assertIn('not allowed', result['reason'])

    def test_validate_directive_missing_file(self):
        missing = os.path.join(self.tmpdir.name, 'missing.yaml')
        with patch.object(validator, 'DIRECTIVES_PATH', missing):
            validator._loaded_directives = None
            result = validator.validate_directive({'agent': 'exec', 'directive': 'run'})
            self.assertFalse(result['is_valid'])
            self.assertIn('not allowed', result['reason'])

    def test_validate_directive_missing_keys(self):
        path = self.create_config({'exec': {'allowed_directives': ['run']}})
        with patch.object(validator, 'DIRECTIVES_PATH', path):
            validator._loaded_directives = None
            result = validator.validate_directive({'directive': 'run'})
            self.assertFalse(result['is_valid'])
            self.assertIn('Missing', result['reason'])


if __name__ == '__main__':
=======
class TestValidator(unittest.TestCase):
    """Scaffold tests for directive validation."""

    def setUp(self):
        """Set up test fixtures."""
        pass

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test_valid_directive(self):
        """Validate a permitted directive."""
        pass

    def test_invalid_directive(self):
        """Reject a directive not allowed for the agent."""
        pass

    def test_missing_directive_file(self):
        """Handle missing configuration gracefully."""
        pass

    def test_missing_keys_in_payload(self):
        """Handle payloads lacking required fields."""
        pass


if __name__ == "__main__":
    unittest.main()
