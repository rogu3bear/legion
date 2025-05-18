import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys
import types

# Provide minimal stubs for optional dependencies
yaml_stub = types.ModuleType("yaml")
yaml_stub.dump = lambda data, f, **kw: __import__('json').dump(data, f)
yaml_stub.safe_load = lambda f: __import__('json').load(f)
sys.modules.setdefault("yaml", yaml_stub)
yaml = yaml_stub
orch_stub = types.ModuleType("legion.orchestrator")
class _DummyOrchestrator: ...
orch_stub.Orchestrator = _DummyOrchestrator
sys.modules.setdefault("legion.orchestrator", orch_stub)

from legion.middleware import run_middleware_pipeline, validator


def setup_directives(tmp_dir: Path) -> Path:
    path = tmp_dir / "directives.yaml"
    with open(path, "w") as f:
        yaml.dump({"agent": {"allowed_directives": ["ok"]}}, f)
    return path


def patch_config(path: Path):
    patcher = patch.object(validator, "DIRECTIVES_PATH", str(path))
    patcher.start()
    validator._loaded_directives = None
    return patcher


def patch_agent_feed_and_therapist(result):
    patches = [
        patch("legion.middleware.post_agent_feed"),
        patch("legion.middleware.therapist_validate", return_value=result),
    ]
    for p in patches:
        p.start()
    return patches


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_pipeline_success(self):
        tmp_path = Path(self.temp_dir.name)
        path = setup_directives(tmp_path)
        cfg_patch = patch_config(path)
        patches = patch_agent_feed_and_therapist({"valid": True, "directive": "ok"})
        result = run_middleware_pipeline(
            {"agent": "agent", "directive": "ok", "confidence": 0.9}, confidence_threshold=0.75
        )
        cfg_patch.stop()
        for p in patches:
            p.stop()
        self.assertTrue(result["final_valid"])
        self.assertEqual(result["source"], "all_middleware_approved")

    def test_pipeline_invalid_directive(self):
        tmp_path = Path(self.temp_dir.name)
        path = setup_directives(tmp_path)
        cfg_patch = patch_config(path)
        patches = patch_agent_feed_and_therapist({"valid": True, "directive": "ok"})
        result = run_middleware_pipeline(
            {"agent": "agent", "directive": "bad", "confidence": 0.9}, confidence_threshold=0.75
        )
        cfg_patch.stop()
        for p in patches:
            p.stop()
        self.assertFalse(result["final_valid"])
        self.assertEqual(result["source"], "validator")

    def test_pipeline_low_confidence(self):
        tmp_path = Path(self.temp_dir.name)
        path = setup_directives(tmp_path)
        cfg_patch = patch_config(path)
        patches = patch_agent_feed_and_therapist({"valid": False, "reason": "low confidence"})
        result = run_middleware_pipeline(
            {"agent": "agent", "directive": "ok", "confidence": 0.5}, confidence_threshold=0.75
        )
        cfg_patch.stop()
        for p in patches:
            p.stop()
        self.assertFalse(result["final_valid"])
        self.assertEqual(result["source"], "therapist")


if __name__ == "__main__":
    unittest.main()
