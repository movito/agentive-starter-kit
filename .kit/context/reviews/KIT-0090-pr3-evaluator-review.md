# KIT-0090 PR 3 — Evaluator Review Record

**PR**: #110 (stacked on #109 → #108) — evaluator provisioning + KIT-0079
**Date**: 2026-08-06
**Ordering**: trio run BEFORE PR open

## Rounds

- **code-reviewer-fast**: CONCERNS — malformed-quote .env robustness
  and `_check_declared` strictness repeats (declined, PR-2
  dispositions); package-absent path (covered by the inline-fallback
  design).
- **code-reviewer (o3)**: CONCERNS — (1) option-shaped config.yml
  library pin could reach `git clone --branch` as a git option:
  **taken** (4bbed8a — tag-shaped validation, letters allowed, with a
  negative test); (2) package-less planning repos fall back to the
  frozen pyproject-only reader: **recorded as the accepted phase-1
  state** — identical to pre-KIT-0079 behavior, `--ref` still works,
  fully resolved once the package publishes (PR 4) and installs
  (phase 2/3).

## Scope decision raised

The spec's PR 3 also listed preflight/review-input/worktree-lib —
three bash surfaces (~1,370 lines). Ported code is a rewrite, not an
extraction; deferred to a follow-on PR and flagged in PR #110's body
for the planner/operator (handoff rule: raise sequencing pressure,
never silently merge phases).

## Verification

Full suite 1033 passed / 12 skipped; CI green on head 4bbed8a via
dispatched run 31142745417; BugBot clean, zero threads.
