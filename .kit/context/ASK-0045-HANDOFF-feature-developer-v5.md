# ASK-0045: Fix Linear Sync Import Paths — Implementation Handoff

**You are the feature-developer-v5. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-03-25
**From**: Planner2
**To**: feature-developer-v5
**Task**: .kit/tasks/2-todo/ASK-0045-linear-sync-test-imports.md
**Status**: Ready for implementation
**Evaluation**: APPROVED by arch-review-fast (Gemini, $0.003)

---

## Task Summary

Fix broken import paths in Linear sync utilities after the v0.4.0 scripts restructure. The production code in `scripts/optional/linear_sync_utils.py` imports from `scripts.logging_config` which no longer exists — it moved to `scripts.core.logging_config` in v0.4.0. This cascades to all 31 tests in `test_linear_sync.py`.

## Current Situation

- **31 tests failing** in `tests/test_linear_sync.py` (all due to import cascade)
- Tests are deselected in CI via `deselect` in `pyproject.toml`, so CI passes but coverage is broken
- Pre-existing on main since v0.4.0 release (2026-03-09)

## Your Mission

1. Fix the import path in `scripts/optional/linear_sync_utils.py`
2. Check and fix `scripts/optional/sync_tasks_to_linear.py` for the same issue
3. Fix any stale imports in `tests/test_linear_sync.py`
4. Verify all 31 tests pass (or are properly skip-marked for external service deps)
5. Remove the `deselect` entries from `pyproject.toml` if tests now pass
6. Ensure full test suite still passes

## Root Cause (Verified)

```
scripts/optional/linear_sync_utils.py:25:
    from scripts.logging_config import setup_logging
    -> ModuleNotFoundError: No module named 'scripts.logging_config'

Fallback on line 27:
    from logging_config import setup_logging
    -> ModuleNotFoundError: No module named 'logging_config'

Correct import should be:
    from scripts.core.logging_config import setup_logging
```

## Files to Inspect and Modify

1. **`scripts/optional/linear_sync_utils.py`** — fix `from scripts.logging_config` -> `from scripts.core.logging_config`; update fallback to `from scripts.core.logging_config`
2. **`scripts/optional/sync_tasks_to_linear.py`** — check for same broken import pattern
3. **`tests/test_linear_sync.py`** — fix any test-side import paths referencing old locations
4. **`pyproject.toml`** — check for `deselect` entries that skip these tests; remove if fixed

## Critical Implementation Details

### 1. Preserve the try/except Pattern

The module uses a try/except for imports to support dual execution (as module and standalone). Preserve this pattern:

```python
try:
    from scripts.core.logging_config import setup_logging
except ImportError:
    from scripts.core.logging_config import setup_logging  # standalone fallback
```

Or simplify if the fallback path is no longer needed.

### 2. No Logic Changes

This is purely an import path fix. Do NOT modify any sync logic, test logic, or add new features.

### 3. Verification Commands

```bash
# Before (expect 31 failures):
python3.13 -m pytest tests/test_linear_sync.py -v

# After (expect 0 failures, some skips OK):
python3.13 -m pytest tests/test_linear_sync.py -v

# Full suite:
python3.13 -m pytest tests/ -v
```

## Acceptance Criteria

- [ ] `scripts/optional/linear_sync_utils.py` imports from `scripts.core.logging_config`
- [ ] `scripts/optional/sync_tasks_to_linear.py` checked/fixed
- [ ] All `test_linear_sync.py` tests pass or are properly skip-marked
- [ ] Full test suite passes (`pytest tests/ -v`)
- [ ] CI passes cleanly
- [ ] No changes to actual sync logic

## Time Estimate

**Estimated**: 30-60 minutes
- Investigation & fix: 15-20 min
- Test verification: 10-15 min
- CI check & PR: 10-20 min

## Evaluation History

- **Evaluator**: arch-review-fast (Gemini 2.5 Flash)
- **Verdict**: APPROVED
- **Cost**: $0.003
- **Finding**: One low-risk note about dual-purpose module design (out of scope for this fix)
- **Log**: `.kit/adversarial/logs/ASK-0045-linear-sync-test-imports--arch-review-fast.md`

## Success Looks Like

- `python3.13 -m pytest tests/test_linear_sync.py -v` shows 0 failures
- `python3.13 -m pytest tests/ -v` shows full suite passing
- CI green on the feature branch
- Clean PR with minimal diff (import path changes only)

---

**Task File**: `.kit/tasks/2-todo/ASK-0045-linear-sync-test-imports.md`
**Evaluation Log**: `.kit/adversarial/logs/ASK-0045-linear-sync-test-imports--arch-review-fast.md`
**Handoff Date**: 2026-03-25
**Coordinator**: Planner2
