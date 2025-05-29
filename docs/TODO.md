<!-- File: docs/TODO.md -->

# Project TODO

This file tracks outstanding cleanup tasks and documentation work.

## Legacy Tests (quarantined)

The following test stubs are marked with `mark_legacy` and should be revisited or removed once ported:

- `tests/core/test_scaffold/test_core_db_import.py`
- `tests/core/test_scaffold/test_core_init_import.py`
- `tests/core/test_scaffold/test_core_utils_import.py`
- `tests/core/test_scaffold/test_indexing_wrapper_import.py`
- `tests/core/test_scaffold/test_migration_import.py`
- `tests/core/test_scaffold/test_network_wrapper_import.py`
- `tests/core/test_priority_queue.py`

## Backlog

These tasks were highlighted in `finalization_report.md` and require follow-up:

- [ ] Remove `legion.core.utils` shim after dependent PRs merge.
- [ ] Add `lychee` link checker to CI for documentation.
- [ ] Consolidate Alembic migration configurations.
- [ ] Validate that no hard-coded ports exist in the codebase.
- [ ] Integrate a documentation linter into GitHub Actions.
- [ ] Add migration rollback tests.
