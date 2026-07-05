# Review Starter: KIT-0037/38/39 — Workflow Hardening Bundle

**PR**: https://github.com/movito/agentive-starter-kit/pull/71
**Branch**: `feature/KIT-0037-38-39-workflow-hardening`
**Prepared**: 2026-07-05 (feature-developer-f5)
**Size**: ~150 additions across 7 files (docs/checklist + code comments; no behavior change)

## What this PR does

Codifies three KIT-0036 retro lessons as durable guardrails, one PR:

1. **KIT-0037 — wrapper exit-code convention**: self-review skill Step 3
   item 8 + Quick Reference row (engine-reserved `0`/`1` never reused for
   wrapper failures; precondition failures → `2`, source-acquisition/I/O
   → `4`). `cmd_sync` audited — all wrapper failure paths already return
   `2` — and annotated (docstring anchor + per-exit-point pointers).
2. **KIT-0038 — `STACKED-PR-WORKFLOW.md`**: when to stack, squash-merge
   vs merge-commit reconciliation (`git rebase --onto`), retarget steps,
   the `edited` ≠ `synchronize` CI gotcha, CodeRabbit's non-default-base
   skip, force-push-blocked branch-replacement fallback. Linked from
   CLAUDE.md's workflow table + PR-SIZE-WORKFLOW.md.
3. **KIT-0039 — scoped-staging self-review item**: Step 3 item 9 + Quick
   Reference row (stage exact paths from a report/manifest, never
   `-A`/`.`/whole roots), citing `_stage_and_commit` and the
   sync-workflow scoped-add loop.

## Key decisions to review

- **DK005 pattern_lint rule NOT implemented** (KIT-0039 optional item).
  Rationale in the PR body: AST linter can't see the shell-in-YAML half
  of the incident surface, and 5 legitimate test-fixture uses would need
  noqa spam. Agree/disagree?
- **Exit-code mapping refinement** (round-2 fix `e5910df`): CodeRabbit
  caught that the retro's shorthand "can't fetch → 2" contradicted
  `resolve_source()`'s actual exit `4`; the docs now state the 2-vs-4
  mapping. The code was always right; only docs changed.

## Review status

- CI: green (lint + 393 tests)
- BugBot: pass, no findings
- CodeRabbit: APPROVED after 1 finding fixed; 1 thread, resolved
- Evaluator: skipped by planner policy (docs-only) — record in
  `.kit/context/reviews/KIT-0037-evaluator-review.md`

## Suggested review path

1. `.kit/skills/self-review/SKILL.md` — items 8 & 9 (the durable guards)
2. `.kit/context/workflows/STACKED-PR-WORKFLOW.md` — command sequences
   match the KIT-0036 retro verbatim
3. `scripts/core/project` — comments/docstring only; confirm no
   behavior change (`git diff main...HEAD -- scripts/core/project`)
