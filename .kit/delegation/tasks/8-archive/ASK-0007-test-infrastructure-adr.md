# ASK-0007: Test Infrastructure Strategy ADR

**Status**: Done
**Priority**: high
**Assigned To**: planner
**Estimated Effort**: 1-2 hours
**Created**: 2025-11-28
**Revised**: 2025-11-28 (scope clarification)

## Related Tasks

**Parent Task**: None (ADR Migration - Tier 1)
**Depends On**: None
**Blocks**: ASK-0019 (Test CI Implementation)
**Related**: ASK-0006 (Adversarial Workflow)

## Overview

Create ADR-0005 documenting the **architectural decision** to adopt pytest-based testing with pre-commit hooks and CI/CD integration. This ADR captures the "why" behind our testing strategy.

**Source**: `thematic-cuts/docs/decisions/adr/ADR-0012-test-infrastructure-strategy.md`

**Why Essential**: Establishes testing expectations for contributors - coverage requirements, TDD workflow, and quality gates.

## Scope Boundaries

### ADR-0005 Scope (This Task)

The ADR documents the **decision and rationale**:

| ADR Covers | Description |
|------------|-------------|
| Problem statement | Need for consistent test infrastructure |
| Decision | Adopt pytest + pre-commit + GitHub Actions |
| Testing strategy | TDD workflow, coverage requirements |
| Quality gates | Pre-commit, CI verification |
| Alternatives considered | Other frameworks, manual testing |
| Consequences | Trade-offs, maintenance overhead |

### NOT in Scope (Separate Task: ASK-0019)

Implementation work is handled by ASK-0019:

| Implementation (ASK-0019) | Description |
|---------------------------|-------------|
| Create test workflow | `.github/workflows/test.yml` |
| Configure coverage threshold | Update `pyproject.toml` |
| Restructure tests (optional) | `tests/unit/`, `tests/integration/` |

### Current Infrastructure State

| Component | Status | Notes |
|-----------|--------|-------|
| pytest | ✅ Configured | `pyproject.toml` with markers |
| pytest-cov | ✅ Installed | In dev dependencies |
| pre-commit | ✅ Configured | Black, isort, flake8, pytest-fast |
| GitHub Actions test workflow | ❌ Missing | Only `sync-to-linear.yml` exists |
| Coverage threshold | ❌ Not enforced | No fail threshold configured |
| Test structure | ⚠️ Flat | `tests/` without unit/integration split |

**Key Principle**: ADR-0005 documents the *strategy* and *decisions*. ASK-0019 implements the missing infrastructure.

## Requirements

### Functional Requirements

1. Create ADR-0005 following project template
2. Document the decision to use pytest + pre-commit + CI
3. Define coverage requirements (80%+ for new code)
4. Explain TDD workflow expectations
5. Reference existing infrastructure and planned improvements

### Non-Functional Requirements

- ADR follows project template structure
- Clear separation from implementation (ASK-0019)
- Actionable guidance for contributors

## Acceptance Criteria

### Must Have

- [ ] ADR-0005 created at `docs/decisions/adr/ADR-0005-test-infrastructure-strategy.md`
- [ ] Follows project ADR template structure
- [ ] Documents problem (inconsistent testing) and solution (pytest stack)
- [ ] Defines coverage expectations (80%+ new code, aspirational)
- [ ] Explains pre-commit hook integration (what runs, when)
- [ ] Documents TDD workflow (Red → Green → Refactor)
- [ ] Lists alternatives considered (other frameworks)
- [ ] Documents consequences (positive, negative, neutral)

### Should Have

- [ ] Example test patterns (brief, not comprehensive)
- [ ] Guidance on test organization (unit vs integration)
- [ ] Reference to ASK-0019 for CI workflow implementation

### Should NOT Have

- [ ] ❌ Implementation of GitHub Actions workflow (ASK-0019)
- [ ] ❌ Changes to pyproject.toml coverage settings (ASK-0019)
- [ ] ❌ Test directory restructuring (ASK-0019)

## Implementation Plan

### Step 1: Review Source Materials (20 min)

1. Read thematic-cuts ADR-0012 (if accessible)
2. Review current infrastructure:
   - `pyproject.toml` - pytest config, markers
   - `.pre-commit-config.yaml` - hooks configuration
   - `tests/` - current test structure

### Step 2: Create ADR-0005 (45-60 min)

Create `docs/decisions/adr/ADR-0005-test-infrastructure-strategy.md` with:

**Context Section:**
- Problem: Need consistent testing approach for starter-kit
- Forces: Multiple contributors, quality assurance, CI/CD integration
- Current state: Partial infrastructure exists

**Decision Section:**
- Adopt pytest as test framework
- Use pre-commit for local quality gates
- Target 80% coverage for new code
- TDD workflow: Red → Green → Refactor

**Consequences Section:**
- Positive: Consistent quality, early bug detection
- Negative: Setup overhead, learning curve
- Neutral: Requires discipline to maintain

**References Section:**
- Link to existing config files
- Link to ASK-0019 for CI implementation

### Step 3: Review and Finalize (15-20 min)

1. Verify no overlap with ASK-0019 scope
2. Ensure all acceptance criteria met
3. Check ADR template compliance

## Success Metrics

### Quantitative

- ADR-0005 created and follows template
- < 200 lines (focused on decisions)
- All "Must Have" acceptance criteria met

### Qualitative

- Contributors understand testing expectations
- Clear separation: ADR = strategy, ASK-0019 = implementation
- New contributors can follow TDD workflow

## Time Estimate

| Phase | Time |
|-------|------|
| Review source materials | 20 min |
| Create ADR-0005 | 45-60 min |
| Review and finalize | 15-20 min |
| **Total** | **1-2 hours** |

## References

- **Source ADR**: `thematic-cuts/docs/decisions/adr/ADR-0012-test-infrastructure-strategy.md`
- **ADR Template**: `docs/decisions/adr/TEMPLATE-FOR-ADR-FILES.md`
- **Existing Infrastructure**:
  - `pyproject.toml` (pytest config)
  - `.pre-commit-config.yaml` (hooks)
  - `tests/` (test files)
- **Implementation Task**: ASK-0019 (Test CI Implementation)

## Notes

- This is a **documentation task**, not implementation
- Starter-kit has partial test infrastructure - document what exists and what's planned
- Coverage threshold is aspirational in ADR; enforcement comes in ASK-0019
- Revised 2025-11-28 to separate ADR from implementation scope

### Evaluator Feedback Addressed (2025-11-28)

**Scope Clarification:**
- ADR-0005 documents the *decision* (why pytest, why 80% coverage, why TDD)
- ASK-0019 handles *implementation* (GitHub Actions workflow, coverage config)
- This separation follows project pattern (ASK-0006 was ADR-only too)

**Coverage Enforcement:**
- ADR documents the *expectation* (80% for new code)
- ASK-0019 implements the *enforcement* (CI workflow with coverage check)

**File Changes:**
- Output: `docs/decisions/adr/ADR-0005-test-infrastructure-strategy.md`
- No changes to pyproject.toml or .github/workflows/ (that's ASK-0019)

---

**Template Version**: 1.0.0
**Created**: 2025-11-28
**Revised**: 2025-11-28
