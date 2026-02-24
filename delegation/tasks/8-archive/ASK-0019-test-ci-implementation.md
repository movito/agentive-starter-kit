# ASK-0019: Test CI/CD Implementation

**Status**: Done
**Priority**: high
**Assigned To**: feature-developer
**Estimated Effort**: 2-3 hours
**Created**: 2025-11-28

## Related Tasks

**Parent Task**: None
**Depends On**: ASK-0007 (Test Infrastructure ADR - for strategy decisions)
**Blocks**: None
**Related**: ASK-0006 (Adversarial Workflow)

## Overview

Implement the GitHub Actions test workflow and coverage configuration for the agentive-starter-kit. This task creates the CI/CD infrastructure that enforces the testing strategy documented in ADR-0005.

**Why Essential**: Currently, the starter-kit has no CI test workflow - only `sync-to-linear.yml` exists. Tests run locally via pre-commit but are not enforced on GitHub. This creates risk of broken code merging.

## Current State

| Component | Status | Gap |
|-----------|--------|-----|
| pytest | ✅ Configured | None |
| pytest-cov | ✅ Installed | Not enforced in CI |
| pre-commit | ✅ Configured | Local only |
| GitHub Actions test workflow | ❌ Missing | **Primary deliverable** |
| Coverage threshold | ❌ Not set | Need fail threshold |
| Test structure | ⚠️ Flat | Optional improvement |

## Requirements

### Functional Requirements

1. Create GitHub Actions workflow for running tests
2. Configure coverage threshold enforcement (80%)
3. Run on pull requests and pushes to main
4. Report coverage in PR comments (optional)

### Non-Functional Requirements

- Workflow completes in < 5 minutes
- Clear failure messages for debugging
- Follows GitHub Actions best practices
- Compatible with existing pre-commit setup

## Acceptance Criteria

### Must Have

- [ ] `.github/workflows/test.yml` created and functional
- [ ] Workflow triggers on PR and push to main/develop
- [ ] Runs pytest with coverage reporting
- [ ] Coverage threshold set to 80% (fail if below)
- [ ] Tests pass on current codebase
- [ ] Workflow uses Python 3.11 (match pyproject.toml)

### Should Have

- [ ] Coverage report uploaded as artifact
- [ ] Cache pip dependencies for faster runs
- [ ] Matrix testing (Python 3.10, 3.11) if beneficial
- [ ] Coverage badge in README

### Could Have

- [ ] PR comment with coverage summary
- [ ] Restructure tests into `unit/` and `integration/` folders
- [ ] Separate fast/slow test jobs

## Implementation Plan

### Step 1: Create Test Workflow (45-60 min)

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run tests with coverage
        run: |
          pytest tests/ -v --cov=. --cov-report=xml --cov-fail-under=80

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage.xml
```

### Step 2: Configure Coverage Threshold (15 min)

Update `pyproject.toml`:

```toml
[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
]
```

### Step 3: Verify and Test (30-45 min)

1. Run tests locally to ensure they pass
2. Check coverage meets 80% threshold
3. Push to branch and verify workflow runs
4. Fix any failures

### Step 4: Optional Enhancements (30-60 min)

If time permits:
- Add coverage badge to README
- Set up PR coverage comments
- Consider test directory restructure

## Success Metrics

### Quantitative

- Workflow created and passing
- Coverage threshold enforced at 80%
- All existing tests pass
- Workflow completes in < 3 minutes

### Qualitative

- Clear CI feedback on PRs
- Contributors know immediately if tests fail
- Coverage visible and tracked

## Time Estimate

| Phase | Time |
|-------|------|
| Create test workflow | 45-60 min |
| Configure coverage | 15 min |
| Verify and test | 30-45 min |
| Optional enhancements | 30-60 min |
| **Total** | **2-3 hours** |

## Technical Details

### Workflow Triggers

```yaml
on:
  push:
    branches: [main, develop]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - 'delegation/**'
  pull_request:
    branches: [main, develop]
```

### Coverage Configuration

Current `pyproject.toml` has:
```toml
[tool.coverage.run]
source = ["."]
omit = ["tests/*", "venv/*", ".venv/*"]
```

Need to add:
```toml
[tool.coverage.report]
fail_under = 80
```

### Test Markers (Already Configured)

```toml
markers = [
    "slow: marks tests as slow (>1s runtime)",
    "integration: integration tests requiring external services",
    "unit: fast unit tests (default)",
]
```

## References

- **Strategy ADR**: ASK-0007 → `docs/decisions/adr/ADR-0005-test-infrastructure-strategy.md`
- **Existing Config**: `pyproject.toml`, `.pre-commit-config.yaml`
- **Current Workflows**: `.github/workflows/sync-to-linear.yml`
- **Test Files**: `tests/test_linear_sync.py`, `tests/test_template.py`

## Notes

- This is an **implementation task** - the strategy is documented in ADR-0005 (ASK-0007)
- Current tests should pass - verify before adding coverage enforcement
- Start with 80% threshold; can adjust if existing code doesn't meet it
- Consider running workflow on a branch first before merging to main

---

**Template Version**: 1.0.0
**Created**: 2025-11-28
