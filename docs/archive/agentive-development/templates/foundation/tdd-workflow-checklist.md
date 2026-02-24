# TDD Workflow Checklist

**Purpose:** Step-by-step guide for RED-GREEN-REFACTOR cycle with test-driven development
**Layer:** Foundation
**Topic:** 1.3 Test-Driven Development Basics
**Estimated Time to Complete:** 15-30 minutes per cycle (varies by feature complexity)

---


## Key Terms

This template uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Task** - Discrete unit of work with clear acceptance criteria
- **Agent** - AI collaborator with a specific role and tool access
- **Template** - Reusable document structure with placeholders
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation

See the [full glossary](../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## When to Use This Checklist

Use this workflow when:
- Starting any new feature or bug fix that involves code changes
- You want to ensure tests are written before implementation (RED-GREEN-REFACTOR)
- You need to maintain test coverage while developing
- You're new to TDD and want a step-by-step guide
- You want to verify you're following the project's mandatory testing workflow

---

## Instructions

1. **Copy this checklist** into your task file or development notes
2. **Work through each section sequentially** - Don't skip RED to jump to GREEN
3. **Check off items as you complete them** - This helps track progress
4. **Commit after each color** - RED commit, GREEN commit, REFACTOR commit
5. **Repeat the cycle** - One cycle per test case or feature slice
6. **Keep cycles small** - Aim for 15-30 minutes per RED-GREEN-REFACTOR cycle

**Important:** This is a mandatory workflow for all code changes in this project. Use `SKIP_TESTS=1 git commit` only for WIP commits (document why).

---

## The Template

```markdown
# TDD Workflow: [FEATURE NAME]

**Feature:** [Brief description]
**Test file:** `tests/test_[module_name].py`
**Module under test:** `[module_path]`
**Started:** YYYY-MM-DD HH:MM
**Estimated cycles:** [Number of RED-GREEN-REFACTOR cycles needed]

---

## Pre-TDD Setup

Before starting the RED-GREEN-REFACTOR cycle:

- [ ] Test environment is ready (pytest installed, runs successfully)
- [ ] Know what you're testing (clear requirement or acceptance criterion)
- [ ] Identified edge cases and error scenarios
- [ ] Copied `tests/test_template.py` as starting point (if new test file)
- [ ] Test file location: `tests/test_[module_name].py` created
- [ ] Imports added (module under test, pytest, fixtures)

**Requirement being tested:**
[Write the specific requirement, user story, or acceptance criterion]

**Edge cases identified:**
1. [Edge case 1 - e.g., "empty input"]
2. [Edge case 2 - e.g., "invalid data type"]
3. [Edge case 3 - e.g., "boundary condition"]

---

## Cycle 1: [TEST CASE NAME]

### 🔴 RED: Write Failing Test

**Test description:** [What behavior are you testing?]

- [ ] Test file created or opened: `tests/test_[module].py`
- [ ] Test function named descriptively: `test_[what_it_tests]`
- [ ] Test follows AAA pattern:
  - [ ] **Arrange:** Set up test data and conditions
  - [ ] **Act:** Call the function/method being tested
  - [ ] **Assert:** Verify the expected outcome
- [ ] Test has clear, descriptive name (explains what's tested and expected outcome)
- [ ] Run test: `pytest tests/test_[module].py::test_[name] -v`
- [ ] **Verify test FAILS for the right reason** (not syntax error, but expected failure)
- [ ] Commit failing test: `git add tests/ && git commit -m "test: Add failing test for [feature]"`

**Test code:**
```python
def test_[descriptive_name]:
    """[Docstring explaining what this tests]"""
    # Arrange
    [setup_code]

    # Act
    [call_function]

    # Assert
    [verify_outcome]
```

**Failure message (expected):**
```
[Copy the actual pytest failure output here]
```

**Committed:** ✅ Commit hash: [git commit hash]

---

### 🟢 GREEN: Make It Pass (Minimal Implementation)

**Implementation approach:** [Simplest solution to make test pass]

- [ ] Implement the **simplest** solution that makes the test pass (no over-engineering)
- [ ] Avoid adding features not covered by tests
- [ ] Run test: `pytest tests/test_[module].py::test_[name] -v`
- [ ] **Verify test PASSES** ✅
- [ ] Run all tests in module: `pytest tests/test_[module].py -v`
- [ ] **Verify no regressions** (all other tests still pass)
- [ ] Commit passing implementation: `git add . && git commit -m "feat: Implement [feature] to pass test"`

**Implementation code:**
```python
# [module_path]
def [function_name]:
    """[Docstring]"""
    [implementation]
```

**Test result:**
```
✅ test_[name] PASSED
```

**Committed:** ✅ Commit hash: [git commit hash]

---

### 🔵 REFACTOR: Improve Code Quality

**Refactoring goals:**
- [ ] Remove duplication (DRY principle)
- [ ] Improve variable/function naming (clarity)
- [ ] Extract helper functions if needed (single responsibility)
- [ ] Add type hints if missing (Python 3.7+)
- [ ] Improve code comments (explain "why", not "what")
- [ ] Check code formatting: `black [module_path]`
- [ ] Run all tests: `pytest tests/test_[module].py -v`
- [ ] **Verify tests still pass** ✅ (refactoring should not break tests)
- [ ] Commit refactored code: `git add . && git commit -m "refactor: Improve [what] in [module]"`

**Refactoring changes made:**
1. [Change 1 - e.g., "Extracted helper function calculate_total()"]
2. [Change 2 - e.g., "Renamed variable x to user_count for clarity"]
3. [Change 3 - e.g., "Removed duplicate validation logic"]

**Committed:** ✅ Commit hash: [git commit hash]

---

## Cycle 2: [NEXT TEST CASE NAME]

<!-- Repeat RED-GREEN-REFACTOR for next test case -->

### 🔴 RED: Write Failing Test
[Same structure as Cycle 1]

### 🟢 GREEN: Make It Pass
[Same structure as Cycle 1]

### 🔵 REFACTOR: Improve Code Quality
[Same structure as Cycle 1]

---

## Cycle 3: [EDGE CASE OR ERROR HANDLING]

<!-- Repeat for edge cases and error scenarios -->

---

## Post-TDD: Iteration Decision

After completing all planned cycles:

- [ ] All happy path scenarios covered by tests? ✅ Yes / ❌ No
- [ ] All edge cases tested? ✅ Yes / ❌ No
- [ ] Error handling tested (invalid input, exceptions)? ✅ Yes / ❌ No
- [ ] Boundary conditions tested (min/max values, empty collections)? ✅ Yes / ❌ No
- [ ] Test coverage check: `pytest tests/test_[module].py --cov=[module] --cov-report=term-missing`
- [ ] Coverage meets target (80%+ for new code)? ✅ Yes / ❌ No

**Coverage result:**
```
[Paste pytest-cov output here]
```

**Decision:**
- ✅ **Feature complete** - All scenarios covered, moving to next feature
- ❌ **More tests needed** - Return to RED step for: [list scenarios]

---

## Pre-Commit Verification

Before committing your final changes:

- [ ] All tests pass: `pytest tests/test_[module].py -v`
- [ ] Full test suite passes: `pytest tests/ -v`
- [ ] No xfail tests introduced (unless documented with reason)
- [ ] Coverage maintained or improved
- [ ] Code formatted: `black .` and `isort .`
- [ ] Pre-commit hooks pass (run automatically on `git commit`)

**If pre-commit hook blocks commit:**
Fix the issues identified, then retry commit.

**For WIP commits only** (use sparingly):
```bash
SKIP_TESTS=1 git commit -m "WIP: [reason for skipping tests]"
```

---

## Pre-Push Verification (MANDATORY)

Before pushing to remote:

- [ ] **MANDATORY:** Run `./scripts/ci-check.sh`
- [ ] All checks pass (tests, coverage, hooks)
- [ ] No uncommitted changes (clean working tree)
- [ ] Branch is up to date with main (if applicable)
- [ ] Push to remote: `git push origin [branch-name]`

**ci-check.sh prevents 80%+ of CI failures.** Always run it before pushing.

---

```

---

## Usage Examples

This workflow was used for:

1. **[TASK-2025-0012: Precision Timecode Fixes](../../../delegation/tasks/completed/TASK-2025-012-timeline-offset.md)**
   - Feature: Fix 86-frame error at 23.976fps
   - Cycles: 4 RED-GREEN-REFACTOR cycles (happy path, edge cases, boundary conditions, error handling)
   - Result: 100% precision test pass rate (54/54 tests), zero cumulative error
   - Time: ~2 hours (estimated 3 hours, TDD saved time by catching edge cases early)

2. **[API Test Suite: test_process.py](../../../tests/api/test_process.py)**
   - Feature: FastAPI /process endpoint with comprehensive error handling
   - Cycles: 22 test cases (11 success scenarios, 11 error scenarios)
   - Result: 156/158 tests passing (98.7%), 92% coverage
   - Pattern: Each error type got its own RED-GREEN-REFACTOR cycle

3. **[GUI Processor Tests: test_processor.py](../../../tests/test_gui/test_processor.py)**
   - Feature: CLI processor with format detection and validation
   - Cycles: 29 test cases covering all export formats
   - Result: 100% coverage of critical paths, caught 3 bugs before production
   - Learning: TDD revealed format-specific edge cases that would have been missed

---

## Tips

- **Tip 1: Keep RED-GREEN-REFACTOR cycles small** - Aim for 15-30 minutes per cycle. If a cycle takes >1 hour, you're trying to test too much at once. Split into smaller cycles.

- **Tip 2: Don't skip RED** - If your test passes immediately without implementation, you didn't write a good test. The test should fail first, proving it's actually testing the feature.

- **Tip 3: Commit after each color** - This creates a clear history: failing test → passing implementation → improved code. Makes debugging and code review easier.

- **Tip 4: Write the simplest GREEN implementation** - Don't over-engineer in the GREEN phase. "Make it work, then make it better" is the TDD mantra. REFACTOR is where you improve.

- **Tip 5: REFACTOR is not optional** - Many developers skip this step. Don't. Accumulated technical debt from skipped refactoring slows future development.

- **Tip 6: Test one thing per test** - Each test should verify one specific behavior. If a test has multiple assertions testing different things, split into separate tests.

- **Tip 7: Use descriptive test names** - `test_user_login()` is vague. `test_user_login_with_valid_credentials_returns_token()` is clear and self-documenting.

- **Tip 8: AAA pattern improves readability** - Arrange-Act-Assert makes tests easy to understand. Use comments `# Arrange`, `# Act`, `# Assert` to mark sections.

- **Tip 9: Test error cases explicitly** - Don't assume error handling works. Write tests for invalid input, exceptions, and edge cases. These often reveal bugs.

- **Tip 10: Coverage is a guide, not a goal** - 100% coverage doesn't mean bug-free code. Focus on testing behavior and edge cases, not just hitting coverage numbers.

---

**Related:**
- [Concept: Test-Driven Development Basics](../../01-foundation/03-test-driven-development-basics/concept.md)
- [Example: F3 - TDD for Precision Timecode](../../examples/F3-tdd-precision-timecode-TASK-2025-012.md)
- [Template: test_template.py](../../../tests/test_template.py) - AAA pattern examples
- [Workflow: TESTING-WORKFLOW.md](../../../.agent-context/workflows/TESTING-WORKFLOW.md) - Project testing requirements
- [Workflow: COMMIT-PROTOCOL.md](../../../.agent-context/workflows/COMMIT-PROTOCOL.md) - Pre-commit and pre-push requirements
