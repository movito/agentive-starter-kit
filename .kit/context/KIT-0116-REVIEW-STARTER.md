# Review Starter: KIT-0116 Phase 1 — Tier 1 review pipeline + Review Flags

**PR**: https://github.com/movito/agentive-starter-kit/pull/148
**Branch**: `feature/KIT-0116-review-pipeline` @ `44d4854`
**Task**: `.kit/tasks/4-in-review/KIT-0116-automated-review-pipeline.md`
(3-phase arc — this starter covers **Phase 1 / PR 1 only**; Phases 2–3
await your go and will branch from updated main)

## What shipped

| Surface | Change |
|---------|--------|
| `.kit/context/workflows/REVIEW-PIPELINE.md` (NEW, + door twin) | Single value authority: ladder, Review Flags registry, 3-axis tier heuristics (incl. binding KIT-0118 argv axis), evidence contract, governance |
| fd bodies ×2 (2.7.0 / 1.7.0) | New **Phase 5b Native Review Pass** gate (pre-PR /code-review + flagged /security-review, fix-or-defer, persisted record); docs-habit step; fail-closed flag handling |
| planner bodies ×2 (2.2.0 / 1.2.0) | Declare `**Review Flags**:` at spec time; carry in handoffs; cite-never-restate |
| `/preflight` (1.6.0) | **Gate 8: review pass done** — session-checked (`-f && -s`); CLI stays 7-gate by design (PyPI/plugin version-skew decision; mechanization = KIT-0120, new backlog) |
| commit-push-pr (1.2.0), review-handoff skill (1.2.0), review-starter template | Gate counts, bundled-PR third pointer + lead artifact, checklist item |
| TASK-STARTER-TEMPLATE (2.2.0) | Review Flags field shell |
| `tests/test_review_pipeline_contracts.py` (NEW) | Red-first drift greps (observed 11 RED pre-edit); Phase-2 checks arm on `KIT-ADR-0036*.md` existence |

## Review evidence (the ladder, dogfooded on itself)

- **Gate 5**: fast + o3 evaluators (claude-code skipped — no security
  surface, recorded). 11 findings: 5 fixed / 5 rejected-with-
  verification (2 provably wrong) / 1 deferred to Phase 2.
  → `.kit/context/reviews/KIT-0116-evaluator-review.md`
- **Gate 8 / Tier-1 live smoke**: `/code-review medium` ran in-slot
  (session "KIT-0116 FDF5 review pipeline", agent `cccfa7`; ~95k
  tokens, ~5.7 min). 8 findings, **all fixed pre-PR** — notably
  cross-file contract contradictions neither evaluator caught.
  → `.kit/context/reviews/KIT-0116-review-pass.md`
- **Deferred findings**: none.

## Bot round (budget: one substantive round — held)

8 threads (BugBot 2, CodeRabbit 6 across two scans), **all replied +
resolved**: 5 fixed (`test -s` → `-f && -s` regular-file Gate 8 check,
bundled lead review-pass artifact, flag fail-closed union rule), 1
acknowledged (roster refresh = arc-end release, ruling below), 1
declined with KIT-0042/KIT-0114 rationale + KIT-0120 scope line, 1
deferred to Phase 2 (Bash allowlist parsing — format born with the ADR).

## Preflight @ 44d4854

Gates 2–8 PASS (Gate 8 via the new Step 1b — worked first try).
**Gate 1: tests/lint/bots green; ONLY the plugin drift guard is red** —
the expected, ruled shape: rostered components changed, plugin release
cut ONCE at arc end (held-release discipline; planner decides then
whether KIT-0115 / KIT-0103 R6 / KIT-0117 ride the same train).

## Areas for review focus

1. **The Gate-8 layering decision** (session-checked in markdown, CLI
   stays 7-gate): version-skew rationale in the PR body + KIT-0120.
   This is Phase 1's one real architecture call — confirm you agree.
2. **REVIEW-PIPELINE.md heuristics** — the binding third axis is
   encoded per spec Notes; wording is planner-owned from here.
3. **Bodies bind at next launch** — this session ran the OLD workflow
   (by design); the smoke is the proof of the new one.

## Operator next steps

1. Review + merge PR #148 — with **every non-drift check green** (they
   are, at `5f0945d`: tests ×3, lint, both bots). The ONLY red is the
   plugin drift guard, whose expected-red window is documented in
   `.github/workflows/plugin-drift.yml`; justification: KIT-0116 arc
   held-release ruling (handoff §"Twins and the release train") —
   the planner cuts the plugin release ONCE at arc end, superseding
   the same-day default for this arc
2. Say the word for **Phase 2** (Tier 2 + KIT-ADR-0036 + reviewer
   toolset audit + architecture-reviewer) — new branch from updated
   main, announced in-session
3. Or abort the arc here — Phase 1 stands alone by design
