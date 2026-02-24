# ASK-0035: Make Linear Dependencies Optional

**Status**: Todo
**Priority**: medium
**Assigned To**: feature-developer
**Estimated Effort**: 1-2 hours
**Created**: 2026-02-24
**Target Completion**: 2026-02-25

## Related Tasks

**Related**: ASK-0005 (Linear sync infrastructure — original implementation)

## Status History

- **Todo** (from initial) - 2026-02-24 15:10:00

## Overview

Move `gql[requests]` and `python-dotenv` from required dependencies to optional dependencies in `pyproject.toml`. Not all downstream projects use Linear for task management. These dependencies should only be installed when explicitly requested via `pip install -e ".[linear]"`.

**Context**: The starter kit template ships with Linear sync as a core dependency. Downstream projects that don't use Linear still install `gql[requests]` (GraphQL client) and `python-dotenv`, adding unnecessary dependencies and potential version conflicts.

## Requirements

### Functional Requirements

1. **Move dependencies**: In `pyproject.toml`, move `gql[requests]>=3.4.0` and `python-dotenv>=1.0.0` from `[project] dependencies` to `[project.optional-dependencies] linear = [...]`
2. **Graceful imports**: Ensure `scripts/linear_sync.py` handles missing `gql` and `dotenv` with `try/except ImportError` (may already exist — verify)
3. **Test marker**: Ensure `requires_gql` pytest marker correctly skips Linear tests when gql is not installed

### Pre-computed details

**pyproject.toml lines to change** (current state):
- Line 26: `"gql[requests]>=3.4.0",    # GraphQL client for Linear API`
- Line 27: `"python-dotenv>=1.0.0",    # Load .env files`

**Target state** — add after existing `[project.optional-dependencies]` section (if exists) or create new:
```toml
[project.optional-dependencies]
linear = [
    "gql[requests]>=3.4.0",    # GraphQL client for Linear API
    "python-dotenv>=1.0.0",    # Load .env files
]
```

**Pytest marker** (already defined at line 58):
```
"requires_gql: tests requiring gql package for Linear API (skip with '-m \"not requires_gql\"')",
```

## Implementation Plan

### Step 1: Edit pyproject.toml

Remove the two dependencies from `[project] dependencies` and add them under `[project.optional-dependencies]`.

### Step 2: Verify graceful imports in linear_sync.py

Check that `scripts/linear_sync.py` already has `try/except ImportError` guards. If not, add them:

```python
try:
    from gql import Client, gql
    from gql.transport.requests import RequestsHTTPTransport
    HAS_GQL = True
except ImportError:
    HAS_GQL = False
```

### Step 3: Verify tests

```bash
# Core tests should pass without gql installed
pytest tests/ -m "not requires_gql" -v

# All tests should pass with gql installed
pip install -e ".[linear]"
pytest tests/ -v
```

## Acceptance Criteria

### Must Have
- [ ] `gql[requests]` and `python-dotenv` are NOT in `[project] dependencies`
- [ ] Both are listed under `[project.optional-dependencies] linear = [...]`
- [ ] `pip install -e .` succeeds without installing gql
- [ ] `pip install -e ".[linear]"` installs gql and python-dotenv
- [ ] `pytest tests/ -m "not requires_gql"` passes (core tests without gql)
- [ ] All existing tests pass when gql IS installed

## Time Estimate

| Phase | Time |
|-------|------|
| Edit pyproject.toml | 10 min |
| Verify graceful imports | 15 min |
| Test with/without gql | 20 min |
| **Total** | **~45 min** |

## Notes

- The `requires_gql` marker already exists — it just needs to work correctly
- This is a structural change to pyproject.toml — CI exercises the install, so verify CI passes
