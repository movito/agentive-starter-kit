# ASK-0045: Fix Linear Sync Import Paths After v0.4.0 Restructure

**Status**: Todo
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 1-2 hours
**Created**: 2026-03-25
**Updated**: 2026-03-25

## Related Tasks

**Related**: ASK-0042 (scripts restructure — moved scripts to `scripts/optional/`)

## Overview

Linear sync utilities have broken imports after the v0.4.0 scripts restructure. The root cause is in **production code** (`scripts/optional/linear_sync_utils.py`), not just tests — the module tries to import `from scripts.logging_config import setup_logging`, but `logging_config.py` moved to `scripts/core/logging_config.py` in v0.4.0.

**Impact**: 31 test failures in `test_linear_sync.py` (not 11 as initially reported). The failures cascade from the production import error — every test that imports from `linear_sync_utils` fails with `ModuleNotFoundError`.

**Context**: Pre-existing failure on main since v0.4.0. Tests are deselected in CI pre-commit guard (via `deselect` in pyproject.toml) so CI passes, but the actual test coverage is broken.

## Root Cause Analysis (2026-03-25)

```
scripts/optional/linear_sync_utils.py:25:
    from scripts.logging_config import setup_logging
    → ModuleNotFoundError: No module named 'scripts.logging_config'

Fallback on line 27:
    from logging_config import setup_logging
    → ModuleNotFoundError: No module named 'logging_config'

Correct import should be:
    from scripts.core.logging_config import setup_logging
```

This cascades to all 31 tests in `test_linear_sync.py` that import from `linear_sync_utils` or `sync_tasks_to_linear`.

## Requirements

### Functional Requirements
1. Fix import paths in `scripts/optional/linear_sync_utils.py` to reference `scripts.core.logging_config`
2. Fix import paths in `scripts/optional/sync_tasks_to_linear.py` if similarly broken
3. Fix any stale imports in `tests/test_linear_sync.py` that reference old module paths
4. All 31 currently-failing tests should pass (or be properly skip-marked if they require external services like Linear API)
5. No regression in tests that currently pass

### Non-Functional Requirements
1. No changes to the actual sync logic
2. Maintain the try/except import pattern if needed for standalone script execution

## Implementation Plan

### Files to Inspect and Modify

1. **`scripts/optional/linear_sync_utils.py`** — fix `from scripts.logging_config` → `from scripts.core.logging_config`
2. **`scripts/optional/sync_tasks_to_linear.py`** — check for same broken import pattern
3. **`tests/test_linear_sync.py`** — fix any test-side import paths that reference old locations

### Verification

```bash
# Before: 31 failures
python3.13 -m pytest tests/test_linear_sync.py -v

# After: 0 failures (some may be skipped for external service deps)
python3.13 -m pytest tests/test_linear_sync.py -v

# Full suite must still pass
python3.13 -m pytest tests/ -v
```

## Acceptance Criteria

### Must Have
- [ ] `scripts/optional/linear_sync_utils.py` imports from correct path
- [ ] All `test_linear_sync.py` tests pass or are properly skip-marked
- [ ] Full test suite passes (`pytest tests/ -v`)
- [ ] CI passes cleanly
- [ ] No changes to actual sync logic

## Notes

- The try/except import pattern in `linear_sync_utils.py` suggests the script is designed to run both as a module (`python -m scripts.optional.linear_sync_utils`) and standalone. The fix should preserve this flexibility.
- Priority raised from low to medium — 31 broken tests on main is worse than initially assessed.
