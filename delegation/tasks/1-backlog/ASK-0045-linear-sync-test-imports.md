# ASK-0045: Fix Linear Sync Test Import Paths

**Status**: Backlog
**Priority**: low
**Assigned To**: unassigned
**Estimated Effort**: 1-2 hours
**Created**: 2026-03-25

## Related Tasks

**Related**: ASK-0042 (scripts restructure — moved scripts to `scripts/optional/`)

## Overview

`tests/test_linear_sync.py` has 11 failing tests due to stale import paths. The tests import from `scripts.sync_tasks_to_linear` but the module moved to `scripts.optional.sync_tasks_to_linear` in the v0.4.0 restructure (ASK-0042).

**Context**: Pre-existing failure on main. Discovered during issue triage on 2026-03-25. The failing tests are in `TestLinearClient` and `TestSyncIntegration` classes — they're skipped in CI due to the import error but show as failures locally.

## Requirements

### Functional Requirements
1. Fix import paths in `test_linear_sync.py` to reference `scripts.optional.sync_tasks_to_linear`
2. All 11 currently-failing tests should pass (or be properly skip-marked if they require external services)
3. No regression in the 20+ tests that currently pass

## Implementation Plan

### Files to Modify
- `tests/test_linear_sync.py` — update import paths from `scripts.sync_tasks_to_linear` to `scripts.optional.sync_tasks_to_linear`

## Acceptance Criteria

### Must Have
- [ ] All `test_linear_sync.py` tests pass or are properly skip-marked
- [ ] CI passes cleanly (no import errors)
- [ ] No changes to the actual sync logic
