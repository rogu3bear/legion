import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests.middleware.yaml_stub import yaml
from tests.middleware.orchestrator_stub import orchestrator_stub
sys.modules['yaml'] = yaml
sys.modules.setdefault('legion.orchestrator', orchestrator_stub)

from legion.middleware import run_middleware_pipeline, validator


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.feed_patch = patch('legion.middleware.post_agent_feed')
        self.mock_feed = self.feed_patch.start()

    def tearDown(self):
        self.feed_patch.stop()

    def create_config(self, data):
        path = os.path.join(self.tmpdir.name, 'directives.yaml')
        with open(path, 'w') as fh:
            yaml.dump(data, fh)
        return path

    def patch_config(self, path):
        patcher = patch.object(validator, 'DIRECTIVES_PATH', path)
        patched = patcher.start()
        self.addCleanup(patcher.stop)
        validator._loaded_directives = None
        return patched

    def test_pipeline_success(self):
        path = self.create_config({'agent': {'allowed_directives': ['ok']}})
        self.patch_config(path)
        with patch('legion.middleware.therapist_validate', return_value={'valid': True, 'directive': 'ok'}):
            result = run_middleware_pipeline({'agent': 'agent', 'directive': 'ok', 'confidence': 0.9}, confidence_threshold=0.75)
        self.assertTrue(result['final_valid'])
        self.assertEqual(result['source'], 'all_middleware_approved')

    def test_pipeline_invalid_directive(self):
        path = self.create_config({'agent': {'allowed_directives': ['ok']}})
        self.patch_config(path)
        with patch('legion.middleware.therapist_validate', return_value={'valid': True, 'directive': 'bad'}):
            result = run_middleware_pipeline({'agent': 'agent', 'directive': 'bad', 'confidence': 0.9}, confidence_threshold=0.75)
        self.assertFalse(result['final_valid'])
        self.assertEqual(result['source'], 'validator')

    def test_pipeline_low_confidence(self):
        path = self.create_config({'agent': {'allowed_directives': ['ok']}})
        self.patch_config(path)
        with patch('legion.middleware.therapist_validate', return_value={'valid': False, 'reason': 'low confidence'}):
            result = run_middleware_pipeline({'agent': 'agent', 'directive': 'ok', 'confidence': 0.5}, confidence_threshold=0.75)
        self.assertFalse(result['final_valid'])
        self.assertEqual(result['source'], 'therapist')


if __name__ == '__main__':
    unittest.main()
