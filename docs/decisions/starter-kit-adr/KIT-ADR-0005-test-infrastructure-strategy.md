# KIT-ADR-0005: Test Infrastructure Strategy

**Status**: Accepted

**Date**: 2025-11-28

**Deciders**: planner, coordinator

## Context

### Problem Statement

The agentive-starter-kit needs a consistent, automated testing strategy that:
- Ensures code quality across contributions
- Catches bugs before they reach production
- Provides fast feedback during development
- Integrates with CI/CD pipelines

Without a defined strategy, testing becomes inconsistent - some contributors write tests, others don't, coverage varies, and quality gates are unclear.

### Forces at Play

**Technical Requirements:**
- Fast local feedback (tests run in seconds, not minutes)
- Coverage tracking to identify untested code
- Automated checks before commits reach the repository
- Support for both unit and integration tests

**Constraints:**
- Must work with Python 3.9+ (project minimum)
- Should not require complex setup for new contributors
- CI costs should remain minimal (GitHub Actions free tier)
- Must integrate with existing pre-commit workflow

**Assumptions:**
- Contributors have basic pytest familiarity
- Local development uses virtual environments
- GitHub is the primary code hosting platform

## Decision

We adopt **pytest-based testing** with **pre-commit hooks** for local quality gates and **GitHub Actions** for CI/CD verification.

### Core Principles

1. **Test-Driven Development (TDD)**: Write tests first when adding features
   - Red: Write a failing test
   - Green: Write minimal code to pass
   - Refactor: Improve code while keeping tests green

2. **Fast Feedback**: Tests should run quickly during development
   - Pre-commit runs fast tests only (skip slow/integration with markers)
   - Full suite runs in CI

3. **Coverage as Guidance**: Target 80% coverage for new code
   - Coverage is aspirational, not a hard gate (initially)
   - Focus on critical paths and edge cases

4. **Fail Fast**: Catch issues as early as possible
   - Pre-commit prevents bad commits locally
   - CI prevents bad code from merging

### Testing Stack

| Component | Purpose | Configuration |
|-----------|---------|---------------|
| pytest | Test framework | `pyproject.toml` [tool.pytest.ini_options] |
| pytest-cov | Coverage reporting | `pyproject.toml` [tool.coverage.*] |
| pre-commit | Local quality gates | `.pre-commit-config.yaml` |
| GitHub Actions | CI/CD automation | `.github/workflows/test.yml` (ASK-0019) |

### Test Organization

```
tests/
├── test_*.py           # Test files (current flat structure)
├── conftest.py         # Shared fixtures (create as needed)
└── __pycache__/        # Python cache (gitignored)
```

**Test Markers** (defined in `pyproject.toml`):
- `@pytest.mark.unit` - Fast, isolated tests (default)
- `@pytest.mark.integration` - Tests requiring external services
- `@pytest.mark.slow` - Tests taking >1 second
- `@pytest.mark.requires_gql` - Tests requiring `gql` package (Linear sync)

### Optional Dependency Pattern

Scripts with optional dependencies (like `gql` for Linear sync) must handle missing packages gracefully to prevent breaking test collection.

**Problem**: Using `sys.exit(1)` at import time breaks pytest collection:

```python
# ❌ BAD: Breaks test collection when gql not installed
try:
    from gql import Client, gql
except ImportError:
    logger.error("gql package not installed")
    sys.exit(1)  # Kills pytest during import!
```

**Solution**: Defer exit to runtime, use skip markers in tests:

```python
# ✅ GOOD: Graceful handling in module
GQL_AVAILABLE = False
Client = None
gql = None

try:
    from gql import Client, gql
    GQL_AVAILABLE = True
except ImportError:
    pass  # Checked at runtime

class LinearClient:
    def __init__(self, api_key: str):
        if not GQL_AVAILABLE:
            raise ImportError("gql package not installed. Run: pip install gql[requests]")
        # ... rest of init

if __name__ == "__main__":
    if not GQL_AVAILABLE:
        logger.error("❌ Error: gql package not installed")
        sys.exit(1)
    main()
```

```python
# ✅ GOOD: Skip markers in tests
try:
    import gql  # noqa: F401
    GQL_AVAILABLE = True
except ImportError:
    GQL_AVAILABLE = False

requires_gql = pytest.mark.skipif(
    not GQL_AVAILABLE,
    reason="gql package not installed (pip install gql[requests])",
)

@requires_gql
class TestLinearClient:
    ...
```

**Result**: Tests skip gracefully instead of failing during collection.

### Pre-commit Integration

Pre-commit runs automatically before each commit:

```yaml
# .pre-commit-config.yaml (excerpt)
- repo: local
  hooks:
    - id: pytest-fast
      name: Run fast tests (pre-commit guard)
      entry: bash -c '... pytest tests/ -v --tb=short -x -m "not slow" ...'
```

**Skip for WIP commits**: `SKIP_TESTS=1 git commit -m "WIP"`

### Coverage Expectations

| Code Type | Target | Rationale |
|-----------|--------|-----------|
| New features | 80%+ | High coverage for new code |
| Bug fixes | Test the fix | Prevent regression |
| Refactoring | Maintain existing | Don't reduce coverage |
| Scripts/utilities | Best effort | Lower priority |

**Note**: Coverage enforcement (CI fail threshold) is implemented in ASK-0019.

## Consequences

### Positive

- ✅ **Consistent quality**: All code goes through same quality gates
- ✅ **Fast feedback**: Pre-commit catches issues before push
- ✅ **Clear expectations**: Contributors know testing requirements
- ✅ **Regression prevention**: Tests catch breaking changes
- ✅ **Documentation**: Tests serve as executable documentation

### Negative

- ⚠️ **Setup overhead**: New contributors must install pre-commit
- ⚠️ **Learning curve**: TDD requires practice to master
- ⚠️ **Time investment**: Writing tests takes additional time upfront
- ⚠️ **False security**: High coverage doesn't guarantee correctness

### Neutral

- 📊 **Discipline required**: Team must maintain testing culture
- 📊 **Marker usage**: Requires judgment on when to use slow/integration
- 📊 **Coverage debates**: 80% target may need adjustment per project

## Alternatives Considered

### Alternative 1: unittest (Python Standard Library)

**Description**: Use Python's built-in unittest framework instead of pytest.

**Rejected because**:
- ❌ More verbose test syntax (class-based)
- ❌ Less powerful fixtures (no pytest fixtures)
- ❌ Smaller plugin ecosystem
- ❌ pytest is industry standard for Python projects

### Alternative 2: No Pre-commit (CI Only)

**Description**: Only run tests in CI, not locally before commits.

**Rejected because**:
- ❌ Slower feedback loop (wait for CI)
- ❌ More failed CI runs (waste of resources)
- ❌ Issues discovered later are harder to fix
- ❌ Breaks the "fail fast" principle

### Alternative 3: 100% Coverage Requirement

**Description**: Require 100% test coverage for all code.

**Rejected because**:
- ❌ Diminishing returns past ~80%
- ❌ Encourages testing trivial code
- ❌ Can lead to brittle tests
- ❌ Slows development significantly

### Alternative 4: No Coverage Tracking

**Description**: Don't track or enforce coverage at all.

**Rejected because**:
- ❌ No visibility into untested code
- ❌ Coverage tends to decline over time
- ❌ Harder to identify testing gaps
- ❌ Less accountability for test quality

## Related Decisions

- **KIT-ADR-0004**: Adversarial Workflow Integration - Uses testing as verification
- **ASK-0019**: Test CI Implementation - Implements the CI workflow for this strategy

## References

### Infrastructure

- **pytest configuration**: `pyproject.toml` [tool.pytest.ini_options]
- **Coverage configuration**: `pyproject.toml` [tool.coverage.*]
- **Pre-commit hooks**: `.pre-commit-config.yaml`
- **CI Workflow**: `.github/workflows/test.yml` (implemented by ASK-0019)

### External Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [pre-commit documentation](https://pre-commit.com/)
- [TDD by Example (Kent Beck)](https://www.oreilly.com/library/view/test-driven-development/0321146530/)

### Quick Reference

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=. --cov-report=term-missing

# Run fast tests only (skip slow/integration)
pytest tests/ -v -m "not slow and not integration"

# Run specific test file
pytest tests/test_example.py -v

# Install pre-commit hooks
pre-commit install

# Run pre-commit manually
pre-commit run --all-files

# Skip pre-commit tests for WIP
SKIP_TESTS=1 git commit -m "WIP"
```

## Revision History

- 2025-11-28: Initial decision (Accepted)
- 2026-02-01: Added Optional Dependency Pattern for graceful handling of missing packages

---

**Template Version**: 1.1.0
**Last Updated**: 2026-02-01
**Project**: agentive-starter-kit
