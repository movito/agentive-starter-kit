# Testing Workflow

**Purpose**: Run test suites to verify implementation quality
**Agent**: Primarily feature-developer, but all agents should use when needed
**Last Updated**: 2025-11-01

---

## When to Use

- ✅ Before creating any commit
- ✅ After implementing new features or fixes
- ✅ Before marking task as complete
- ✅ When CI/CD failures occur

---

## Commands

```bash
# Run all tests (including slow tests)
pytest tests/ -v

# Run fast tests only (pre-commit subset, ~2 seconds)
pytest tests/ -m "not slow"

# Run slow tests only (integration tests)
pytest tests/ -m slow

# Run specific file
pytest tests/path/to/test_file.py -v

# Run specific test
pytest tests/path/to/test_file.py::test_name -v

# With coverage
pytest tests/ --cov=thematic_cuts --cov-report=term-missing

# Verbose output (shows print statements)
pytest tests/ -vv -s

# Re-run only failed tests
pytest tests/ --lf

# Run tests in parallel
pytest tests/ -n auto
```

---

## Workflow Steps

1. **Run tests**: `pytest tests/ -v`
2. **Review output**: Check pass/fail counts, read error messages
3. **Fix failures**: Address failing tests one by one
4. **Verify no regressions**: Ensure previously passing tests still pass
5. **Check coverage**: Use `--cov` flag to verify new code is tested
6. **Run CI check**: Verify tests pass in GitHub Actions environment

---

## Interpreting Results

| Symbol | Meaning |
|--------|---------|
| ✅ | **Passing** - Green checkmark, test passed |
| ❌ | **Failing** - Red X, test failed (read traceback) |
| ⚠️ | **Xfailed** - Expected failure (marked with `@pytest.mark.xfail`) |
| 🎉 | **Xpassed** - Unexpectedly passing (was expected to fail but now passes) |
| ⏭️ | **Skipped** - Skipped (marked with `@pytest.mark.skip`) |

---

## Pre-Commit Enforcement

**Added**: 2025-11-01 (TASK-2025-045)

Tests now run automatically before every commit via pre-commit hooks:

### Fast Test Subset
- **What runs**: All tests except those marked with `@pytest.mark.slow`
- **Duration**: ~2 seconds (431/433 tests)
- **Coverage**: Catches 80%+ of test failures before commit
- **Tests excluded**: 2 slow integration tests (10s, 4s)

### Usage

**Normal workflow** (tests run automatically):
```bash
git commit -m "feat: Add new feature"
# → Pre-commit hooks run:
#    1. Black (formatting)
#    2. isort (imports)
#    3. flake8 (linting)
#    4. pytest-fast (tests)
# → If tests fail: Commit blocked
```

**Skip for WIP commits** (use sparingly):
```bash
SKIP_TESTS=1 git commit -m "WIP: Work in progress"
# → Tests skipped with warning
# → Commit succeeds
```

### When Tests Fail

If pre-commit hook blocks your commit:
1. **Read the error message** - Shows which test(s) failed
2. **Fix the test failure** - Address the root cause
3. **Try committing again** - Tests will re-run
4. **Last resort**: Use `SKIP_TESTS=1` (document why in commit message)

### Slow Tests

Tests marked with `@pytest.mark.slow`:
- `test_error_handling_cascade` (10.01s - DaVinci API integration)
- `test_check_resolve_connection_failure` (4.01s - timeout test)

These run in CI only, not in pre-commit hooks.

---

## TDD Workflow (Test-First Development)

**Recommended approach for new features**:

Test-Driven Development (TDD) helps catch bugs early and ensures comprehensive test coverage. Follow the Red-Green-Refactor cycle:

### 1. Write failing test first

```bash
# Copy template
cp tests/test_template.py tests/test_my_feature.py

# Edit test file (write test for feature that doesn't exist yet)
# Run test - should fail
pytest tests/test_my_feature.py -v
```

**Expected**: Test fails (RED) because feature not implemented yet.

### 2. Implement feature until test passes

```bash
# Edit implementation code
# Run test again
pytest tests/test_my_feature.py -v
```

**Expected**: Test passes (GREEN) - feature works.

### 3. Refactor while keeping tests green

```bash
# Improve code quality, performance, readability
# Run tests frequently to ensure nothing breaks
pytest tests/test_my_feature.py -v
```

**Expected**: Tests still pass (GREEN) - refactoring didn't break functionality.

### 4. Commit (tests run automatically)

```bash
git add .
git commit -m "feat: add my feature"
# → Pre-commit runs fast tests automatically
# → Commit succeeds if tests pass
```

### TDD Benefits

- ✅ **Prevents bugs**: Catches issues before they reach production
- ✅ **Better design**: Writing tests first leads to cleaner APIs
- ✅ **Documentation**: Tests serve as usage examples
- ✅ **Confidence**: Refactor safely with comprehensive test coverage
- ✅ **Faster debugging**: Know exactly what broke when tests fail

### TDD Template

See `tests/test_template.py` for a ready-to-use template with examples:
- AAA pattern (Arrange, Act, Assert)
- Edge case testing
- Error handling tests
- Parameterized tests
- Slow test markers

---

## Before Push (MANDATORY)

**Always run CI check before pushing to GitHub**:

```bash
./scripts/core/ci-check.sh
```

### What ci-check.sh Does

Runs the **SAME checks** as GitHub Actions CI:
1. ✅ Full test suite (including slow tests)
2. ✅ Coverage check (53%+ threshold)
3. ✅ Pre-commit hooks (formatting, linting)
4. ✅ Uncommitted changes check

**Duration**: ~15-30 seconds (vs waiting minutes for CI feedback)

### Why This Is Mandatory

- **Prevents CI failures**: Catch failures locally before push
- **Faster feedback**: Know immediately if something is broken
- **No email alerts**: Avoid GitHub notification spam
- **100% confidence**: If ci-check passes, CI will pass

### Usage

**Before EVERY push**:
```bash
# Check passes ✅
./scripts/core/ci-check.sh

# Only push if check passes ✅
git push origin main
```

**Recommended alias** (add to `~/.bashrc` or `~/.zshrc`):
```bash
# Add these aliases for convenience
alias gci="./scripts/core/ci-check.sh"
alias gpush="./scripts/core/ci-check.sh && git push origin main"

# Then use:
gpush  # Runs CI check + pushes if passes
```

### When ci-check.sh Fails

If the script fails:
1. **Read error output** - Shows which check failed (tests/coverage/hooks)
2. **Fix the issue** - Address test failures or coverage drops
3. **Run again** - Verify fix with `./scripts/core/ci-check.sh`
4. **Push** - Only after check passes

**DO NOT** bypass ci-check.sh by pushing directly. This defeats the purpose of local verification.

---

## Best Practices

### ✅ DO:
- Run full test suite before committing
- Fix all new failures your code introduces
- Maintain or improve overall pass rate
- Update tests if implementation changes intentionally

### ⚠️ USE CAUTION:
- Don't commit if tests are failing (unless xfailed with justification)
- Don't skip tests without good reason

---

## Documentation

- **Quick Reference**: `.agent-context/PROCEDURAL-KNOWLEDGE-INDEX.md`
- **Full Guide**: This document
- **Test Infrastructure**: See `tests/conftest.py` for fixtures and configuration
- **CI/CD**: `.github/workflows/tests.yml`

---

**Related Workflows**:
- [TEST-SUITE-WORKFLOW.md](./TEST-SUITE-WORKFLOW.md) - Comprehensive test analysis
- [COVERAGE-WORKFLOW.md](./COVERAGE-WORKFLOW.md) - Coverage measurement
- [COMMIT-PROTOCOL.md](./COMMIT-PROTOCOL.md) - Committing after tests pass
