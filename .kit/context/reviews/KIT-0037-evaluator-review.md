# KIT-0037/38/39 — Evaluator Review Record

**Tasks**: KIT-0037 (wrapper exit-code convention), KIT-0038 (stacked-PR
workflow doc), KIT-0039 (scoped-staging self-review item)
**PR**: #71 (`feature/KIT-0037-38-39-workflow-hardening`)
**Date**: 2026-07-05
**Verdict**: SKIPPED by planner policy

## Why skipped

The handoff (`.kit/context/KIT-0037-38-39-HANDOFF-feature-developer.md`,
Evaluation summary) skips adversarial evaluation for this bundle:

- All three tasks are docs/checklist/process codification — the explicit
  planner skip category.
- Every item was independently validated upstream: the KIT-0036 bot
  findings (3 exit-code findings, 2 staging findings) and the KIT-0036
  retro are the evidence base the docs codify.
- The conditional trigger ("if the optional pattern_lint rule becomes
  real logic, run code-reviewer-fast") did NOT fire: the DK005 staging
  heuristic was deliberately not implemented. Rationale in PR #71's
  description — half the incident surface is shell-in-YAML (invisible to
  the AST-based linter) and the repo's five legitimate broad-staging test
  fixtures would need immediate noqa suppression.

## What reviewed the change instead

- CI (lint + full pytest, 393 passed) — green
- Cursor BugBot — pass, no findings
- CodeRabbit — 1 actionable finding (exit `2` vs `4` conflation in the
  new skill item), verified against `resolve_source()` in
  `scripts/core/project`, fixed in `e5910df`; latest review APPROVED,
  all threads resolved
