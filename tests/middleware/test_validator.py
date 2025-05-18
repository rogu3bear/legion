import yaml
from pathlib import Path

from legion.middleware import validator


def setup_directives(tmp_path, data):
    path = tmp_path / "directives.yaml"
    with open(path, "w") as fh:
        yaml.dump(data, fh)
    return path


def test_validate_directive_success(tmp_path, mocker):
    path = setup_directives(tmp_path, {"exec": {"allowed_directives": ["run"]}})
    mocker.patch.object(validator, "DIRECTIVES_PATH", str(path))
    validator._loaded_directives = None

    result = validator.validate_directive({"agent": "exec", "directive": "run"})
    assert result["is_valid"]


def test_validate_directive_invalid(tmp_path, mocker):
    path = setup_directives(tmp_path, {"exec": {"allowed_directives": ["run"]}})
    mocker.patch.object(validator, "DIRECTIVES_PATH", str(path))
    validator._loaded_directives = None

    result = validator.validate_directive({"agent": "exec", "directive": "stop"})
    assert not result["is_valid"]
    assert "not allowed" in result["reason"]


def test_validate_directive_missing_file(tmp_path, mocker):
    missing = tmp_path / "missing.yaml"
    mocker.patch.object(validator, "DIRECTIVES_PATH", str(missing))
    validator._loaded_directives = None

    result = validator.validate_directive({"agent": "exec", "directive": "run"})
    assert not result["is_valid"]
    assert "not allowed" in result["reason"]


def test_validate_directive_missing_keys(tmp_path, mocker):
    path = setup_directives(tmp_path, {"exec": {"allowed_directives": ["run"]}})
    mocker.patch.object(validator, "DIRECTIVES_PATH", str(path))
    validator._loaded_directives = None

    result = validator.validate_directive({"directive": "run"})
    assert not result["is_valid"]
    assert "Missing" in result["reason"]
