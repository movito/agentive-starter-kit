# KIT-0034: Harden preflight Gate 2 + bootstrap/self-review (KIT-0033 retro)

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 2-4 hours
**Created**: 2026-06-27
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0033 (portable downstream agents) — surfaced these in retro
**Related**: KIT-0026 (peer-repo agent/skill sync — same dual-audience boundary)

## Overview

The KIT-0033 retro (`.kit/context/retros/KIT-0033-retro.md`) produced three
process/tooling follow-ups. They are unrelated in code but share a theme:
making the kit's preflight and bootstrap machinery robust against issues that
KIT-0033 hit firsthand. The most impactful is the **preflight Gate 2 false
negative**, which made the PR read as "not ready" even after CodeRabbit
APPROVED with a green check-run and zero open threads.

## Requirements

### Functional Requirements

- **F1 — Relax preflight Gate 2 (CodeRabbit)**: `scripts/core/preflight-check.sh`
  Gate 2 currently FAILs unless a `coderabbitai[bot]` review event is tied to the
  **exact head SHA**. After a docs-only or otherwise trivial push, CodeRabbit
  updates its check-run and keeps an APPROVED review on an earlier SHA without
  re-emitting a review event — so the gate reports a false negative (observed on
  KIT-0033 PR #58). Treat the gate as PASS when **all** hold:
  - CodeRabbit's check-run is passing, AND
  - the latest `coderabbitai[bot]` review verdict is APPROVED (or COMMENTED with
    no unresolved threads), AND
  - there are zero unresolved review threads.
  Keep the strict SHA match as the primary signal; the above is the fallback so a
  green-everywhere PR doesn't read as failing. Mirror the logic for Gate 3
  (BugBot) if it shares the same SHA-exact assumption.

- **F2 — Self-review checklist: downstream-synced tests**: add an explicit item to
  the `self-review` skill (`.kit/skills/`) and/or the feature-developer Phase 4
  checklist: *any new test that imports from `scripts/local/` (which is NOT synced
  to consumers) must be excluded from the consumer `tests/` rsync in
  `bootstrap-consumer.sh`, and should module-skip if its dependency is absent.*
  Both BugBot and CodeRabbit caught this on KIT-0033; a checklist item prevents the
  recurrence for the kit's dual ASK-dev / consumer audience.

- **F3 — Codify the temp-then-commit (two-pass) bootstrap pattern**: document the
  pattern used to fix the KIT-0033 atomicity bug — when a bootstrap step mutates
  multiple files under `set -e`, stage **all** outputs to temp files first, then
  `mv` them into place only after every step succeeds (never per-item `mv` inside
  the loop). Put it in a scripting guideline (e.g. `.kit/context/workflows/` or a
  `docs/` scripting-conventions note) so future bootstrap/sync scripts follow it.

### Non-Functional Requirements

- **N1**: F1 must not weaken the gate for genuinely un-reviewed PRs — a PR with no
  CodeRabbit review at all, or with unresolved threads, must still FAIL.
- **N2**: No new dependencies; preflight stays shell + `gh`.

## Acceptance Criteria

- [ ] `preflight-check.sh` Gate 2 passes on a PR where CodeRabbit's check-run is
  green, latest review is APPROVED, and zero threads are unresolved — even if the
  head SHA has no CodeRabbit review event
- [ ] Gate 2 still FAILs when CodeRabbit has not reviewed at all, or when any
  thread is unresolved
- [ ] (If applicable) Gate 3 BugBot uses the same robust check
- [ ] self-review skill / Phase 4 checklist includes the "downstream-synced test
  must exclude its `scripts/local/` dependency" item
- [ ] A scripting guideline documents the temp-then-commit two-pass pattern with a
  short before/after example
- [ ] Any preflight logic change has test coverage (mock `gh` output) if the script
  has an existing test harness; otherwise a documented manual verification

## Test Plan

- Construct (or mock) the three Gate-2 states: (a) APPROVED + green + 0 threads +
  no head-SHA review → PASS; (b) no review at all → FAIL; (c) unresolved thread →
  FAIL. Verify against KIT-0033 PR #58 as the real-world (a) case.
- Re-run `preflight-check.sh` on a current green PR and confirm no regression on the
  other six gates.

## Notes

- Source: `.kit/context/retros/KIT-0033-retro.md` (Process Actions).
- F1 is the priority and is well-scoped/ready; F2 and F3 are doc/checklist changes
  and could be split out if the planner prefers smaller PRs.
- A fourth, lower-value retro idea (express `kit_markers.py` test-coverage
  expectations in the consumer manifest contract) is intentionally **out of scope**
  here — revisit only if the dual-audience test boundary causes further breakage.
