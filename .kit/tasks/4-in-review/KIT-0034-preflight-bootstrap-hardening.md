# KIT-0034: Harden preflight Gate 2 + bootstrap/self-review (KIT-0033 retro)

**Status**: In Review
**Priority**: high
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
  **Reconfirmed on KIT-0036 PR #63** (2026-07-04): Gate 2 false-negatived again
  on the docs-only review-starter commit (check-run pass + APPROVED on an
  earlier SHA + 0 threads). Second observation — raises priority.

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

- **F4 — Preflight Gate 1 (CI): distinguish "not yet registered" from "failed"**
  *(from the KIT-0032 retro)*. Immediately after a push, `preflight-check.sh`
  Gate 1 reports "no CI runs found for latest commit" and reads as a **FAIL**,
  when in fact GitHub simply has not registered the workflow runs yet (observed
  twice on KIT-0032 PR #56, both false alarms). Treat "no runs found for the head
  SHA" as a distinct **PENDING/UNKNOWN** state — not FAIL — optionally with a
  short bounded re-poll (a few seconds) before reporting. A genuine CI failure
  (a run that completed with `conclusion != success`) must still FAIL. Shares the
  same false-negative theme as F1/F2 and the same file.

- **F5 — Bootstrap KIT-LOCAL marker-membership test** *(from the 2026-07-04
  session retro)*: add a test asserting that every `.claude/agents/*.md`
  containing `KIT-LOCAL` markers is listed in BOTH `KIT_AGENTS` and
  `AGENT_EXCLUDES` in `scripts/local/bootstrap-consumer.sh`. This mechanically
  catches the class of bug BugBot found on PR #66 (new marker-bearing agent not
  wired into bootstrap → kit identity leaks to fresh consumers) and the
  `--no-kit` prune gap CodeRabbit found on PR #68. Since `KIT_AGENTS` is now
  single-sourced and also drives the `--no-kit` prune, one membership assertion
  covers copy-exclusion, marker-merge, and opt-out removal together. Note: this
  test imports/reads `scripts/local/` content, so per F2 it must itself be
  excluded from the consumer `tests/` rsync.

### Non-Functional Requirements

- **N1**: F1 must not weaken the gate for genuinely un-reviewed PRs — a PR with no
  CodeRabbit review at all, or with unresolved threads, must still FAIL.
- **N2**: No new dependencies; preflight stays shell + `gh`.
- **N3**: F4 must not let a real CI failure pass as "pending" — only the
  *absence of any run for the head SHA* maps to PENDING; a completed non-success
  run still FAILs.

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
- [ ] Gate 1 reports PENDING/UNKNOWN (not FAIL) when no CI run exists yet for the
  head SHA, and still FAILs on a completed non-success run
- [ ] Any preflight logic change has test coverage (mock `gh` output) if the script
  has an existing test harness; otherwise a documented manual verification
- [ ] A test asserts every KIT-LOCAL-marker-bearing agent file is present in both
  `KIT_AGENTS` and `AGENT_EXCLUDES` in `bootstrap-consumer.sh`, and that test is
  excluded from the consumer `tests/` rsync

## Test Plan

- Construct (or mock) the three Gate-2 states: (a) APPROVED + green + 0 threads +
  no head-SHA review → PASS; (b) no review at all → FAIL; (c) unresolved thread →
  FAIL. Verify against KIT-0033 PR #58 as the real-world (a) case.
- Re-run `preflight-check.sh` on a current green PR and confirm no regression on the
  other six gates.

## Notes

- Source: `.kit/context/retros/KIT-0033-retro.md` (F1–F3 Process Actions),
  `.kit/context/retros/KIT-0032-retro.md` (F4 — preflight Gate 1), and
  `.kit/context/retros/SESSION-2026-07-04-agent-maintenance-retro.md` (F5 —
  bootstrap marker-membership test). F4 was added here rather than in KIT-0035
  so all `preflight-check.sh` changes land together; F5 was added here (per that
  retro's own pointer) so all bootstrap-hardening lands together.
- F1 is the priority and is well-scoped/ready; F2 and F3 are doc/checklist changes
  and could be split out if the planner prefers smaller PRs.
- A fourth, lower-value retro idea (express `kit_markers.py` test-coverage
  expectations in the consumer manifest contract) is intentionally **out of scope**
  here — revisit only if the dual-audience test boundary causes further breakage.

## Evaluation (2026-07-04)

`arch-review-fast` (gemini-2.5-flash): **REVISION_SUGGESTED** — log:
`.adversarial/logs/KIT-0034-preflight-bootstrap-hardening--arch-review-fast.md`.
Planner disposition:

- **Declined — "migrate preflight to Python"**: contradicts the deliberate N2
  constraint (shell + `gh`, no new deps). `preflight-check.sh` is 412 lines; a
  language migration is a separate architectural decision, not a hardening fix.
  If a future task grows preflight further, revisit via ADR.
- **Accepted — "invest in `gh` output mocking / validate parsed output"**:
  folded into the existing test-coverage acceptance criterion. Note there is
  currently NO test harness for `preflight-check.sh` or
  `bootstrap-consumer.sh`, so the documented-manual-verification fallback
  applies to gate logic; F5's marker-membership test IS automatable (pytest,
  reads both files as text).
- **Noted — "declarative dual-audience boundary config"**: valid long-term
  idea; overlaps KIT-0026/KIT-0031 territory. Out of scope here.
- **Accepted — F3 pattern must be prominently documented**: already the F3
  requirement; no change.
