# TASK-[ID]: [Task Title]

<!-- INSTRUCTION: Replace [ID] with your task identifier (e.g., 2025-042, FEATURE-123)
     Replace [Task Title] with a concise description (e.g., "Add User Authentication") -->

**Status**: [Not Started | In Progress | Completed | Blocked]
**Priority**: [Critical | High | Medium | Low]
**Assigned To**: [Agent name or developer name]
**Created**: YYYY-MM-DD
**Estimated Time**: [X hours or days]
**Dependencies**: [List any tasks this depends on, or "None"]

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

## Executive Summary

<!-- INSTRUCTION: 1-2 sentences explaining WHAT this task accomplishes and WHY it matters.
     Focus on user value or business impact, not implementation details. -->

[Brief summary of the task goal and its importance]

---

## Context

<!-- INSTRUCTION: Explain the background and motivation.
     - What problem are we solving?
     - Why is this task necessary now?
     - What's the current state?
     - What will change after this task? -->

**Problem Statement:**
[Describe the problem or opportunity this task addresses]

**Current State:**
[What exists today? What's working? What's not?]

**Desired State:**
[What will exist after this task is complete?]

**Why Now:**
[Why is this task prioritized at this time?]

---

## Implementation Plan

<!-- INSTRUCTION: Break the work into discrete steps.
     Be specific about files, functions, and changes.
     Order steps logically (dependencies first, integration last). -->

### Phase 1: [Phase Name]

#### Task 1.1: [Task Name]
**Description:** [What needs to be done]
**Files affected:** [List files to create/modify]
**Key changes:**
- [Bullet point 1]
- [Bullet point 2]

#### Task 1.2: [Task Name]
**Description:** [What needs to be done]
**Files affected:** [List files to create/modify]
**Key changes:**
- [Bullet point 1]
- [Bullet point 2]

### Phase 2: [Phase Name]
[Continue as needed...]

---

## TDD Workflow (Mandatory)

<!-- INSTRUCTION: Delete this section if task is documentation-only or no code changes.
     For all code changes, follow Red-Green-Refactor cycle. -->

1. **Before coding**: Copy `tests/test_template.py` → `tests/test_[feature_name].py`
2. **Red**: Write failing test(s) for the feature
3. **Green**: Implement until tests pass
4. **Refactor**: Improve code while keeping tests green
5. **Commit**: Pre-commit hook runs tests automatically

**Starting point:** `tests/test_template.py` (use AAA pattern examples)

---

## Test Requirements

<!-- INSTRUCTION: Specify concrete test expectations.
     What scenarios must be tested? What edge cases matter? -->

### Unit Tests
- [ ] Test [core functionality scenario 1]
- [ ] Test [core functionality scenario 2]
- [ ] Test [edge case 1]
- [ ] Test [edge case 2]
- [ ] Test [error handling scenario]

### Integration Tests (if applicable)
- [ ] Test [end-to-end workflow 1]
- [ ] Test [end-to-end workflow 2]
- [ ] Test [system interaction scenario]

### Performance Tests (if applicable)
- [ ] Test [performance requirement - e.g., "response time <200ms"]
- [ ] Mark slow tests with `@pytest.mark.slow`

---

## Test Coverage Requirements

<!-- INSTRUCTION: Keep these requirements for code changes.
     Adjust percentages based on your project standards. -->

- [ ] **New code**: 80%+ line coverage
- [ ] **Overall coverage**: Maintain or improve baseline (e.g., ≥53%)
- [ ] **Critical paths**: 100% coverage
- [ ] **Test file location**: `tests/test_[module_name].py`

**Verification:**
```bash
pytest tests/test_[feature_name].py -v --cov=[module_name] --cov-report=term-missing
```

---

## Pre-Commit/Pre-Push Requirements (Mandatory)

<!-- INSTRUCTION: These are mandatory for all tasks. Don't remove this section. -->

### Pre-Commit (Automatic)
- ✅ Tests run automatically on commit (fast tests only, ~2s)
- ✅ Formatting and linting enforced
- ℹ️ Skip with `SKIP_TESTS=1 git commit` (use sparingly, document reason)

### Pre-Push (Manual - MANDATORY)
```bash
# MUST run before EVERY push
./scripts/ci-check.sh

# Only push if check passes
git push origin [branch-name]
```

**Why mandatory:**
- Catches 80%+ of CI failures locally
- Faster feedback than waiting for CI
- Prevents broken builds in main branch

---

## Success Criteria

<!-- INSTRUCTION: Define OBJECTIVE measures of success.
     Good: "All tests pass", "API returns <200ms p95", "Coverage >80%"
     Bad: "Code looks good", "Feature is done", "Works well" -->

### Must Have (Required for completion)
- [ ] [Criterion 1 - measurable]
- [ ] [Criterion 2 - measurable]
- [ ] [Criterion 3 - measurable]
- [ ] All tests passing (no xfail unless documented)
- [ ] Test coverage meets requirements
- [ ] Pre-push check (`ci-check.sh`) passes

### Nice to Have (Optional enhancements)
- [ ] [Enhancement 1]
- [ ] [Enhancement 2]

---

## Constraints and Assumptions

<!-- INSTRUCTION: Document limitations and things you're assuming.
     Be explicit about trade-offs and known issues. -->

**Constraints:**
- [Constraint 1 - e.g., "Must maintain backward compatibility"]
- [Constraint 2 - e.g., "Cannot add new dependencies"]
- [Constraint 3 - e.g., "Must complete within 8 hours"]

**Assumptions:**
- [Assumption 1 - e.g., "Database schema remains unchanged"]
- [Assumption 2 - e.g., "API v2 will remain stable"]
- [Assumption 3 - e.g., "User authentication is already implemented"]

**Trade-offs:**
- [Trade-off 1 - e.g., "Prioritizing speed over perfection"]
- [Trade-off 2 - e.g., "Simple solution now, optimize later if needed"]

---

## Risk Assessment

<!-- INSTRUCTION: Identify potential problems and mitigation strategies.
     If you mention a risk, provide a mitigation plan. -->

### Risk 1: [Risk Description]
**Probability:** [High | Medium | Low]
**Impact:** [High | Medium | Low]
**Mitigation:** [What will you do to prevent or handle this?]

### Risk 2: [Risk Description]
**Probability:** [High | Medium | Low]
**Impact:** [High | Medium | Low]
**Mitigation:** [What will you do to prevent or handle this?]

---

## Rollback Plan

<!-- INSTRUCTION: How do you undo this if it goes wrong?
     Important for production changes or risky modifications. -->

If this task fails or causes issues:

1. **Immediate rollback:** [Steps to undo changes quickly]
2. **Data recovery:** [How to restore data if needed, or "N/A"]
3. **Communication:** [Who to notify and how]
4. **Git recovery:** `git revert [commit-hash]` or `git reset --hard [commit-hash]`

---

## Documentation Updates

<!-- INSTRUCTION: List documentation that needs updating.
     Keep docs in sync with code changes. -->

- [ ] Update [document name] with [what changed]
- [ ] Add entry to CHANGELOG.md
- [ ] Update [other relevant docs]
- [ ] Add code comments for complex logic
- [ ] Update API documentation (if applicable)

---

## Definition of Done

<!-- INSTRUCTION: Checklist of everything required before marking task complete.
     Should align with Success Criteria. -->

- [ ] All implementation phases complete
- [ ] All tests written and passing
- [ ] Test coverage requirements met
- [ ] Pre-push check (`ci-check.sh`) passes
- [ ] Documentation updated
- [ ] Code reviewed (if applicable)
- [ ] Changes committed with clear message
- [ ] Success criteria verified
- [ ] Rollback plan tested (if high-risk)
- [ ] Task marked complete in tracking system

---

## Notes and Decisions

<!-- INSTRUCTION: Document significant decisions and their rationale.
     Useful for future reference and code archaeology. -->

**Decision Log:**

**[Date]**: [Decision made]
- **Context:** [Why this decision was needed]
- **Options considered:** [What alternatives were evaluated]
- **Decision:** [What was chosen and why]
- **Trade-offs:** [What we're accepting as a consequence]

---

## Related Documents

<!-- INSTRUCTION: Link to relevant context, specs, designs, or prior work. -->

- **Related tasks:** [Links to dependent or related tasks]
- **Design documents:** [Links to technical designs or specs]
- **Prior art:** [Links to similar implementations or examples]
- **References:** [Links to documentation, articles, or resources]

---

**Template Version:** 1.0.0
**Last Updated:** 2025-11-14
**Adapted From:** this project task template

<!-- INSTRUCTION: Remove this comment block before using the template -->
