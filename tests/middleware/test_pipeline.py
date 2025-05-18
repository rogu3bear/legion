import yaml
from legion.middleware import run_middleware_pipeline, validator


def setup_directives(tmp_path):
    path = tmp_path / "directives.yaml"
    yaml.dump({"agent": {"allowed_directives": ["ok"]}}, open(path, "w"))
    return path


def patch_config(mocker, path):
    mocker.patch.object(validator, "DIRECTIVES_PATH", str(path))
    validator._loaded_directives = None


def patch_agent_feed(mocker):
    mocker.patch("legion.middleware.post_agent_feed")


def test_pipeline_success(tmp_path, mocker):
    path = setup_directives(tmp_path)
    patch_config(mocker, path)
    patch_agent_feed(mocker)
    result = run_middleware_pipeline(
        {"agent": "agent", "directive": "ok", "confidence": 0.9}, confidence_threshold=0.75
    )
    assert result["final_valid"]
    assert result["source"] == "all_middleware_approved"


def test_pipeline_invalid_directive(tmp_path, mocker):
    path = setup_directives(tmp_path)
    patch_config(mocker, path)
    patch_agent_feed(mocker)
    result = run_middleware_pipeline(
        {"agent": "agent", "directive": "bad", "confidence": 0.9}, confidence_threshold=0.75
    )
    assert not result["final_valid"]
    assert result["source"] == "validator"


def test_pipeline_low_confidence(tmp_path, mocker):
    path = setup_directives(tmp_path)
    patch_config(mocker, path)
    patch_agent_feed(mocker)
    result = run_middleware_pipeline(
        {"agent": "agent", "directive": "ok", "confidence": 0.5}, confidence_threshold=0.75
    )
    assert not result["final_valid"]
    assert result["source"] == "therapist"
