# Test Suite Workflow

**Purpose**: Execute and analyze test suites for quality assurance
**Agent**: Primarily test-runner, but feature-developer should also use
**Last Updated**: 2025-11-01

---

## When to Use

- ✅ When assigned test verification tasks
- ✅ After feature-developer completes implementation
- ✅ When investigating test failures or regressions
- ✅ Before approving code for merge

---

## Commands

```bash
# Full test suite
pytest tests/ -v

# With coverage
pytest tests/ --cov=thematic_cuts --cov-report=term-missing --cov-report=html

# Specific module
pytest tests/path/to/module/ -v

# Parallel execution (faster)
pytest tests/ -n auto -v

# Verbose with print output
pytest tests/ -vv -s

# Re-run failed tests first
pytest tests/ --lf -v

# Show 10 slowest tests
pytest tests/ --durations=10
```

---

## Workflow Steps

1. **Baseline**: Run full test suite, record pass/fail counts
2. **Analysis**: Identify failing tests, categorize by type
   - Regressions (used to pass, now fail)
   - Expected failures (marked xfail)
   - New bugs (never worked)
3. **Investigation**: For each failure, read traceback, understand root cause
4. **Verification**: Run targeted tests (`--lf` flag) to confirm fixes
5. **Coverage**: Check coverage report, identify untested code paths
6. **Reporting**: Create test results document in `tests/results/` or `.kit/context/`
7. **Recommendation**: Approve merge, request fixes, or escalate to coordinator

---

## Interpreting Test Results

### Metrics to Track:

```
Total tests: 350
Passing: 298 (85.1%)
Failing: 2 (0.6%)
Xfailed: 43 (12.3%)
Xpassed: 0 (0.0%)
Skipped: 7 (2.0%)
```

### Quality Thresholds:

| Pass Rate | Status | Tests Passing |
|-----------|--------|---------------|
| ≥98% | ✅ Excellent | 343+/350 |
| ≥95% | ✅ Good | 333+/350 |
| ≥90% | ⚠️ Acceptable | 315+/350 |
| <90% | ❌ Needs Work | <315/350 |

### Regression Detection:

Compare current pass rate to baseline:
- **Baseline**: 298/350 (85.1%)
- **After change**: 285/350 (81.4%)
- **Result**: ❌ **Regression detected** (13 tests failed)

---

## Best Practices

### ✅ DO:
- Always establish baseline before testing changes
- Document all test results with metrics
- Investigate unexpected xpassed tests (may indicate fixed bugs)
- Use `--lf` flag to re-run only failed tests during debugging
- Check coverage reports to identify gaps
- Report findings in structured format (pass rate, regressions, recommendations)

### ❌ DON'T:
- Don't approve merges with regressions
- Don't skip investigation of new failures
- Don't ignore xpassed tests (they may need xfail markers removed)

---

## Test Results Document Template

```markdown
# Test Results: TASK-YYYY-####

**Date**: YYYY-MM-DD
**Agent**: test-runner
**Branch**: feature/branch-name

## Summary

- **Total Tests**: 350
- **Passing**: 298 (85.1%)
- **Failing**: 2 (0.6%)
- **Xfailed**: 43 (12.3%)
- **Baseline**: 298/350 (85.1%)
- **Change**: 0 tests (no regression ✅)

## Failing Tests

### test_module.py::test_function_name
- **Status**: ❌ FAILING
- **Root Cause**: Assertion error in line 123
- **Action**: Fix required before merge

### test_other.py::test_another
- **Status**: ❌ FAILING
- **Root Cause**: Missing dependency
- **Action**: Add dependency to requirements

## Coverage Analysis

- **Overall**: 53% (baseline maintained ✅)
- **New Code**: 78% (acceptable ✅)
- **Gaps**: See coverage report for details

## Recommendation

❌ **DO NOT MERGE**: 2 failing tests must be fixed first
✅ **APPROVE**: All tests passing, no regressions
⚠️ **REQUEST FIXES**: See failing tests above
```

---

## Documentation

- **Quick Reference**: `.kit/context/PROCEDURAL-KNOWLEDGE-INDEX.md`
- **Full Guide**: This document
- **Coverage Analysis**: [COVERAGE-WORKFLOW.md](./COVERAGE-WORKFLOW.md)
- **Test Infrastructure**: `tests/conftest.py`

---

**Related Workflows**:
- [TESTING-WORKFLOW.md](./TESTING-WORKFLOW.md) - Basic testing commands
- [COVERAGE-WORKFLOW.md](./COVERAGE-WORKFLOW.md) - Coverage measurement
- [TASK-COMPLETION-PROTOCOL.md](./TASK-COMPLETION-PROTOCOL.md) - Handoff creation
