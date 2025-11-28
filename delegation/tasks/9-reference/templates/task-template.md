# TASK-YYYY-NNNN: [Task Title]

**Status**: [Choose ONE: Backlog | Todo | In Progress | In Review | Done | Canceled]
<!-- Status Values (Linear-native):
- Backlog: Task defined but not ready to start
- Todo: Ready to start, dependencies met
- In Progress: Actively being worked on
- In Review: Implementation complete, under review
- Done: Fully complete and verified
- Canceled: Will not be implemented

For blocked tasks, use:
**Status**: Blocked
**Blocked By**: [THEMATIC-NNNN or clear blocker description]
-->
**Priority**: critical | high | medium | low
**Assigned To**: [agent-name]
**Estimated Effort**: X-Y days/hours
**Created**: YYYY-MM-DD
**Target Completion**: YYYY-MM-DD
**Linear ID**: THM-XX (automatically backfilled after first sync)

## Related Tasks

**Parent Task**: THEMATIC-NNNN (Task Title) [if this task was decomposed from a larger task]
**Depends On**: THEMATIC-NNNN, THEMATIC-MMMM [tasks that must complete before this one]
**Blocks**: THEMATIC-PPPP, THEMATIC-QQQQ [tasks that cannot start until this completes]
**Related**: THEMATIC-RRRR, THEMATIC-SSSS [tasks in the same initiative/theme]

<!-- Related Tasks Section:
Use this section to show relationships between tasks. This replaces the old approach
of creating subtasks with suffixes like THEMATIC-NNNN-A, THEMATIC-NNNN-B.

Guidelines:
- If a task becomes too large, decompose it into multiple INDEPENDENT tasks
- Each task gets its own THEMATIC-NNNN ID (not THEMATIC-NNNN-A suffixes)
- Use "Parent Task" to link back to the original task
- Use "Depends On" for sequential dependencies
- Use "Blocks" to show what's waiting on this task
- Use "Related" for tasks in the same initiative but no hard dependencies

Example (Task Decomposition):
  Original: THEMATIC-0100 (too large)
  Decomposed into:
    - THEMATIC-0200 (Part 1) → Parent Task: THEMATIC-0100
    - THEMATIC-0201 (Part 2) → Parent Task: THEMATIC-0100, Depends On: THEMATIC-0200
    - THEMATIC-0202 (Part 3) → Parent Task: THEMATIC-0100, Depends On: THEMATIC-0201

Each task is independent, trackable in Linear, and shows clear relationships.
See: Subtask → Linked Task Conversion (2025-11-25)
-->

## Status History

- **[Status]** (from [Previous Status]) - YYYY-MM-DD HH:MM:SS

<!-- Status History Section:
This section is automatically maintained by task-monitor.py when you move task files
between folders. Each entry shows:
- New status (in bold)
- Previous status (in parentheses)
- Timestamp in ISO 8601 format (YYYY-MM-DD HH:MM:SS)

Entries are in reverse chronological order (newest first). Do not edit manually.
See: THEMATIC-0113, scripts/task-monitor.py
-->

## Overview

[1-2 paragraph description of the task. What needs to be done and why it matters.]

**Context**: [Background information, related work, or upstream dependencies]

**Related Work**: [Links to related tasks, ADRs, or previous investigations]

## Requirements

### Functional Requirements
1. [Requirement 1 - specific, measurable]
2. [Requirement 2 - specific, measurable]
3. [Requirement 3 - specific, measurable]

### Non-Functional Requirements
- [ ] Performance: [Specific targets]
- [ ] Reliability: [Specific targets]
- [ ] Security: [Specific considerations]
- [ ] Maintainability: [Code quality standards]

## TDD Workflow (Mandatory)

**Test-Driven Development Approach**:

1. **Before coding**: Copy `tests/test_template.py` → `tests/test_<feature>.py`
2. **Red**: Write failing tests for feature (describe expected behavior)
3. **Green**: Implement minimum code until tests pass
4. **Refactor**: Improve code while keeping tests green
5. **Commit**: Pre-commit hook runs tests automatically

**TDD Benefits for this task**:
- [Benefit 1 - e.g., "Ensures API contract stability"]
- [Benefit 2 - e.g., "Catches edge cases early"]
- [Benefit 3 - e.g., "Documents expected behavior"]

### Test Requirements
- [ ] Unit tests for all new functions/classes
- [ ] Integration tests for workflows
- [ ] Error handling tests for edge cases
- [ ] Performance tests for critical paths (mark @pytest.mark.slow)
- [ ] Edge case tests: [List specific edge cases]

**Test files to create**:
- `tests/test_<feature>.py` - Main test suite
- `tests/integration/test_<feature>_integration.py` - Integration tests (if needed)

## Test Coverage Requirements

**Coverage Targets**:
- [ ] New code: **80%+ line coverage** (mandatory)
- [ ] Overall coverage: **≥53%** (maintain baseline)
- [ ] Critical paths: **100% coverage** (mandatory)
- [ ] Error paths: **80%+ coverage**

**Coverage Verification**:
```bash
# Check coverage for new files
pytest tests/test_<feature>.py --cov=your_project/<module> --cov-report=term-missing

# Verify no coverage regression
pytest tests/ --cov=thematic_cuts --cov-report=term --cov-fail-under=53
```

**Critical Paths** (require 100% coverage):
1. [Critical path 1 - e.g., "Data validation logic"]
2. [Critical path 2 - e.g., "Error handling for user input"]
3. [Critical path 3 - e.g., "File save operations"]

## Pre-Commit/Pre-Push Requirements (Mandatory)

### Before Every Commit
```bash
git add .
git commit -m "message"
# → Pre-commit hook runs automatically:
#    1. Black (formatting)
#    2. isort (imports)
#    3. flake8 (linting)
#    4. pytest (fast tests)
```

**If tests fail**: Commit is blocked. Fix issues and retry.

**WIP commits only** (use sparingly):
```bash
SKIP_TESTS=1 git commit -m "WIP: work in progress"
```

### Before Every Push (MANDATORY)
```bash
# MANDATORY: Run full CI check locally
./scripts/ci-check.sh

# Only push if ci-check passes
git push origin main
```

**What ci-check.sh does**:
- ✅ Full test suite (including slow tests)
- ✅ Coverage threshold check (53%+)
- ✅ Pre-commit hooks verification
- ✅ Uncommitted changes check

**Benefits**: Prevents 80%+ of CI failures, faster feedback than waiting for GitHub Actions.

**Recommended alias** (add to ~/.bashrc or ~/.zshrc):
```bash
alias gpush="./scripts/ci-check.sh && git push origin main"
```

## Implementation Plan

### Files to Modify

1. `path/to/file1.py` - [Description]
   - Function/class: `function_name()` or `ClassName`
   - Change: [What will be modified]
   - Lines: ~XXX-YYY (if known)

2. `path/to/file2.py` - [Description]
   - Function/class: `function_name()` or `ClassName`
   - Change: [What will be modified]

### Files to Create

1. `path/to/new_file.py` - [Description]
   - Purpose: [Why this file is needed]
   - Contains: [What classes/functions]
   - Estimated lines: ~XXX

2. `tests/test_new_file.py` - [Description]
   - Test coverage for new_file.py
   - Estimated tests: ~XX tests

### Approach

**Step 1: [Phase Name] (Day 1 or X hours)**

[Description of what happens in this step]

**TDD cycle**:
1. Write tests: [Specific tests to write]
2. Run tests (should fail): `pytest tests/test_<feature>.py -v`
3. Implement feature: [What to implement]
4. Run tests (should pass): `pytest tests/test_<feature>.py -v`
5. Refactor if needed

**Implementation details**:
```python
# Pseudocode or key code structure
class NewFeature:
    def method_name(self):
        # Implementation approach
        pass
```

**Step 2: [Phase Name] (Day 2 or Y hours)**

[Repeat structure from Step 1]

**Step 3: [Phase Name] (Day 3 or Z hours)**

[Repeat structure from Step 1]

## Acceptance Criteria

### Must Have ✅
- [ ] All functional requirements implemented
- [ ] All tests passing (no xfail removals without fixes)
- [ ] Coverage targets met (80%+ new code, 53%+ overall)
- [ ] No regressions in existing tests
- [ ] Code follows project style guide
- [ ] Documentation updated (if user-facing)

### Should Have 🎯
- [ ] Performance meets targets
- [ ] Error messages are clear and actionable
- [ ] Edge cases handled gracefully
- [ ] Code is well-commented

### Nice to Have 🌟
- [ ] Additional optimizations
- [ ] Extra test coverage beyond targets
- [ ] Proactive error prevention

## Success Metrics

### Quantitative
- Test pass rate: [Target percentage]
- Coverage increase: [Target percentage points]
- Performance: [Specific timing targets]
- LOC added/modified: [Estimate]

### Qualitative
- Code review feedback: [Expected quality level]
- User experience: [Expected impact]
- Maintainability: [Expected improvement]

## Risks & Mitigations

### Risk 1: [Description]
**Likelihood**: High | Medium | Low
**Impact**: High | Medium | Low
**Mitigation**:
- [Mitigation strategy 1]
- [Mitigation strategy 2]

### Risk 2: [Description]
**Likelihood**: High | Medium | Low
**Impact**: High | Medium | Low
**Mitigation**:
- [Mitigation strategy 1]
- [Mitigation strategy 2]

## Rollback Plan

If implementation causes critical issues:

1. **Immediate**: [Quick rollback steps]
2. **Verification**: [How to verify rollback succeeded]
3. **Root cause**: [How to investigate what went wrong]
4. **Prevention**: [How to prevent similar issues]

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Investigation & Planning | X hours | [ ] |
| TDD: Write failing tests | X hours | [ ] |
| TDD: Implement features | X hours | [ ] |
| TDD: Refactor & optimize | X hours | [ ] |
| Documentation | X hours | [ ] |
| Testing & Validation | X hours | [ ] |
| Code review & fixes | X hours | [ ] |
| **Total** | **X-Y hours** | [ ] |

## References

### Testing & Development
- **TDD Template**: `tests/test_template.py`
- **Testing Workflow**: `.agent-context/workflows/TESTING-WORKFLOW.md`
- **Commit Protocol**: `.agent-context/workflows/COMMIT-PROTOCOL.md`
- **Pre-commit Config**: `.pre-commit-config.yaml`

### Documentation
- **Related ADRs**: [List relevant ADRs]
- **Related Tasks**: [List related tasks]
- **External References**: [Any external docs/links]

## Notes

[Any additional notes, context, or considerations]

---

## FOR API TASKS: Add This Section

## API Testing Requirements (ADR-0035)

**Consumer-First Testing Approach**:

API tests must validate from the **consumer perspective**, not just implementation correctness.

### Required Test Categories

1. **Contract Tests** (`tests/api/contracts/`)
   - [ ] Validate responses against OpenAPI spec
   - [ ] Test all endpoints with valid requests
   - [ ] Test all error responses match spec
   - [ ] Verify response schema compliance

2. **Consumer Tests** (`tests/api/consumers/`)
   - [ ] Test from Swift app perspective
   - [ ] Test from Electron app perspective
   - [ ] Test from CLI perspective
   - [ ] Verify responses work with consumer parsers

3. **Quality Tests** (`tests/api/quality/`)
   - [ ] No null pollution (no unnecessary null fields)
   - [ ] Minimal responses (no bloated data)
   - [ ] Consistent field presence rules
   - [ ] Response size efficiency

4. **Version Tests** (`tests/api/versions/`)
   - [ ] Test all supported API versions
   - [ ] Verify backward compatibility
   - [ ] Test version migration paths

### API Test Coverage Targets
- [ ] All endpoints: 100% coverage
- [ ] All error codes: 100% coverage
- [ ] All API versions: 100% coverage
- [ ] Consumer scenarios: 80%+ coverage

### API Testing Commands
```bash
# Run all API tests
pytest tests/api/ -v

# Run contract validation
pytest tests/api/contracts/ -v

# Run quality checks
pytest tests/api/quality/ -v

# Verify against OpenAPI spec
pytest tests/api/test_openapi_compliance.py -v
```

### References
- **ADR-0035**: `docs/decisions/adr/ADR-0035-separate-api-testing-infrastructure.md`
- **OpenAPI Spec**: `openapi/api-YYYY-MM-DD.yaml` (if applicable)
- **API Testing Guide**: `.agent-context/workflows/API-TESTING-WORKFLOW.md` (if exists)

---

**Template Version**: 1.0.0
**Created**: 2025-11-13
**Last Updated**: 2025-11-13
**Maintained By**: coordinator (tycho)
