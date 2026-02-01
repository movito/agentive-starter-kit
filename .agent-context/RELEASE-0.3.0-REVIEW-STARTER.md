# Review Starter: Release v0.3.0

**Branch**: `feature/ask-0029-multi-evaluator-architecture`
**Target**: `main`
**Prepared by**: Planner
**Date**: 2026-02-01

## Review Scope

This is a **release review** for v0.3.0. The branch contains two completed tasks plus release preparation.

### Included Tasks

1. **ASK-0028**: Project Setup Command (previously reviewed, APPROVED)
2. **ASK-0029**: Multi-Evaluator Architecture (previously reviewed, APPROVED Round 2)

### Release Changes

- CHANGELOG.md: `[Unreleased]` → `[0.3.0] - 2026-02-01`
- pyproject.toml: `version = "0.3.0"`
- README.md: Footer version updated

## Files to Review

### Core Implementation (ASK-0029)

| File | Change |
|------|--------|
| `scripts/project` | `install-evaluators` command (~100 lines) |
| `.adversarial/evaluators/README.md` | Custom evaluator documentation |
| `.adversarial/config.yml.template` | Deprecated `evaluator_model` field |
| `.claude/agents/planner.md` | Provider-agnostic language |
| `.claude/agents/onboarding.md` | Evaluator setup phase |
| `tests/test_project_script.py` | 6 new unit tests |

### Core Implementation (ASK-0028)

| File | Change |
|------|--------|
| `scripts/project` | `setup` command (~80 lines) |
| `tests/test_project_script.py` | Setup command tests |

### Release Files

| File | Change |
|------|--------|
| `CHANGELOG.md` | v0.3.0 release notes |
| `pyproject.toml` | Version bump to 0.3.0 |
| `README.md` | Footer version + date |

### Supporting Changes

| File | Change |
|------|--------|
| `scripts/sync_tasks_to_linear.py` | `GQL_AVAILABLE` pattern (ASK-0028 fix) |
| `tests/test_linear_sync.py` | `@requires_gql` marker |
| `docs/decisions/starter-kit-adr/KIT-ADR-0005-test-infrastructure-strategy.md` | Optional dependency pattern |

## Review Focus

1. **Version Consistency**: Verify 0.3.0 appears consistently across files
2. **CHANGELOG Accuracy**: Entries match actual implementation
3. **No Debug Code**: No leftover debugging or TODO comments
4. **Provider-Agnostic**: No hard-coded model names (GPT-4o) in user-facing docs

## Prior Reviews

Both tasks were previously reviewed and approved:
- ASK-0028: `.agent-context/reviews/ASK-0028-review.md` (APPROVED)
- ASK-0029: `.agent-context/reviews/ASK-0029-review-round2.md` (APPROVED)

This review focuses on **release readiness** rather than re-reviewing implementation.

## Commands

```bash
# View full diff from main
git diff main...HEAD

# Run tests
pytest tests/ -v

# Check CI locally
./scripts/ci-check.sh

# View commits in this branch
git log main..HEAD --oneline
```

## Expected Verdict

- **APPROVED**: Release is ready, can merge to main and tag
- **CHANGES_REQUESTED**: Issues found, fix before release
- **ESCALATE_TO_HUMAN**: Significant concerns requiring user decision

---

**Invoke code-reviewer agent in a new tab with this context.**
