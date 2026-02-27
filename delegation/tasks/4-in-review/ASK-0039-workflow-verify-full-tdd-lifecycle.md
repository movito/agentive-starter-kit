# ASK-0039: Workflow Verification — Full TDD Lifecycle (All 9 Phases)

**Status**: In Review
**Priority**: medium
**Assigned To**: feature-developer-v3
**Estimated Effort**: 1-2 hours
**Created**: 2026-02-27
**Depends On**: ASK-0037, ASK-0038

## Purpose

**This is a verification task.** Its primary goal is to exercise ALL 9 phases of the
v3 workflow on a real Python code change with TDD. This is the comprehensive test —
if this task completes successfully, the upgraded workflow is validated.

### Workflow Phases Exercised

| Phase | Tool | What We're Testing |
|-------|------|--------------------|
| 1. Pre-implementation | `pre-implementation` skill | Pattern lookup, API audit |
| 2. Start | `/start-task` | Branch + task move |
| 3. Implement (TDD) | Manual | Write tests first, then implementation |
| 4. Self-review | `self-review` skill | Input boundary audit |
| 5. Commit/PR | `/commit-push-pr` | Full 7-step flow |
| 6. Bot review | `/check-bots`, `bot-triage` skill | Real bot findings on Python code |
| 7. Evaluator | `code-review-evaluator` skill | Adversarial evaluator run |
| 8. Preflight | `/preflight` | All 7 gates |
| 9. Review handoff | `review-handoff` skill | Review starter + retro |

**ALL phases exercised.** No skips.

## Overview

Add a new lint rule `DK004` to `scripts/pattern_lint.py`: detect bare `except Exception`
clauses that silently swallow errors without logging or re-raising.

**Context**: `pattern_lint.py` currently has 2 rules (DK001: str.replace for extensions,
DK003: string containment on identifiers). Adding DK004 exercises TDD (write tests first),
AST manipulation (same pattern as existing rules), and the full review pipeline.

## Requirements

### Functional Requirements

1. Add rule `DK004` to `scripts/pattern_lint.py`:
   - **Detects**: `except Exception` (or `except BaseException`) followed by `pass`
     or an empty body — i.e., silently swallowed exceptions
   - **Does NOT flag**: `except Exception as e: logger.error(...)` (logged)
   - **Does NOT flag**: `except Exception: raise` (re-raised)
   - **Does NOT flag**: `except Exception as e: return ...` (explicit return)
   - **Suppressed by**: `# noqa: DK004` comment on the except line
   - **Message**: `"Bare 'except {type}' with pass/empty body silently swallows errors. Log, re-raise, or add '# noqa: DK004'."`

2. Add tests in `tests/test_pattern_lint.py` (create if it doesn't exist):
   - Test that DK004 catches `except Exception: pass`
   - Test that DK004 catches `except BaseException: pass`
   - Test that DK004 does NOT flag `except Exception as e: logger.error(e)`
   - Test that DK004 does NOT flag `except Exception: raise`
   - Test that DK004 does NOT flag lines with `# noqa: DK004`
   - Test that DK004 does NOT flag `except ValueError: pass` (specific exceptions are OK)

3. Register DK004 in the `lint_file()` function alongside DK001 and DK003

4. Update the module docstring to list DK004

### Non-Functional Requirements

1. Follow AST-based approach (consistent with DK001/DK003 — no regex)
2. Tests must run via `pytest tests/test_pattern_lint.py -v`
3. Pattern lint must still pass on existing codebase after adding DK004
4. All existing tests must still pass

## Acceptance Criteria

- [ ] DK004 rule implemented in `scripts/pattern_lint.py`
- [ ] Tests written BEFORE implementation (TDD)
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Pattern lint clean on existing code: `python3 scripts/pattern_lint.py scripts/*.py`
- [ ] CI passes (`/check-ci`)
- [ ] Bot reviews received and triaged
- [ ] Code-review evaluator run (`.adversarial/inputs/ASK-0039-*` created)
- [ ] Evaluator review persisted (`.agent-context/reviews/ASK-0039-evaluator-review*.md`)
- [ ] Review starter created (`.agent-context/ASK-0039-REVIEW-STARTER.md`)
- [ ] Preflight check run (`/preflight`) — document which gates pass/fail

## Verification Criteria (Workflow Health)

After completion, check:

- [ ] Pre-implementation skill: loaded, found `patterns.yml`, produced checklist
- [ ] TDD: tests were written before implementation (check git log order)
- [ ] Self-review skill: loaded, produced boundary audit output
- [ ] `/commit-push-pr`: PR created with proper description
- [ ] `/check-bots`: returned real bot status for Python changes
- [ ] `bot-triage` skill: loaded if bots had findings, guided reply/resolve
- [ ] `code-review-evaluator` skill: loaded, template found at `.adversarial/templates/`
- [ ] Evaluator CLI: `adversarial` command ran successfully (or documented failure)
- [ ] `/preflight`: all 7 gates evaluated (document pass/fail for each)
- [ ] `review-handoff` skill: created review starter
- [ ] `/retro`: generated retrospective with metrics
- [ ] No "file not found" or "command not found" errors during workflow

## Shell Script Hardening Checklist

- [ ] N/A — this task modifies Python only

## Output Contract

| Artifact | Location | Required |
|----------|----------|----------|
| DK004 implementation | `scripts/pattern_lint.py` | Yes |
| DK004 tests | `tests/test_pattern_lint.py` | Yes |
| Evaluator input | `.adversarial/inputs/ASK-0039-*` | Yes |
| Evaluator review | `.agent-context/reviews/ASK-0039-evaluator-review*.md` | Yes |
| Review starter | `.agent-context/ASK-0039-REVIEW-STARTER.md` | Yes |
| Retro | In chat (session output) | Yes |

## Notes

- **Agent**: Use `feature-developer-v3` — this exercises the FULL workflow
- **This is the comprehensive test**: If all 9 phases complete without errors,
  the v3 workflow is validated for agentive-starter-kit
- **Evaluator may fail**: If `adversarial` CLI is not configured or API keys
  are missing, document the failure. This tells us whether evaluator setup
  needs additional work.
- **Depends on ASK-0037 and ASK-0038**: Those verify basic workflow first.
  This task assumes the foundation works.
- **If workflow breaks**: Document EXACTLY which phase, skill, or command failed,
  what error was shown, and what the agent tried to do. This is the most
  important output of this task.

## Review

- **PR**: https://github.com/movito/agentive-starter-kit/pull/22
- **Review Starter**: `.agent-context/ASK-0039-REVIEW-STARTER.md`
- **Evaluator Review**: `.agent-context/reviews/ASK-0039-evaluator-review.md`
- **CI**: All 3 runs passed (commits 71f1065, 93ab1a9, a8c1d69)
- **Bot Threads**: 6 total, 6 resolved, 0 unresolved
- **Commits**: 3 (feat, chore-artifacts, fix-bugbot)
