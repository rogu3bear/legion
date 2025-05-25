from pathlib import Path


def test_migration_head_present():
    versions = list(Path('legion/orchestrator/migrations/versions').glob('*.py'))
    assert any('20240601_mcp_init' in v.stem for v in versions)
