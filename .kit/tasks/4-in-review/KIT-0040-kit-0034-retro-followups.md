# KIT-0040: KIT-0034 retro follow-ups — preflight test harness, move-metadata pairing, kit_markers fixes

**Status**: In Review
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 3-5 hours
**Created**: 2026-07-05
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0034 (preflight/bootstrap hardening) — surfaced these in retro
**Related**: KIT-0033 (kit_markers.py origin), KIT-0037/0038/0039 (sibling
retro-follow-up tasks in the v0.8.0 hardening arc)

## Overview

The KIT-0034 retro (`.kit/context/retros/KIT-0034-retro.md`) produced three
follow-ups: turn the session's throwaway stub-`gh` verification matrix into
CI regression coverage, stop `project move` from stranding stale paths in
coordination metadata, and fix two real BugBot findings that have sat
unresolved on merged PR #58 since the KIT-0033 merge.

## Requirements

### Functional Requirements

- **F1 — pytest harness for `preflight-check.sh` gate logic**: a test that
  places a fake `gh` executable on PATH and runs the **real**
  `scripts/core/preflight-check.sh` against canned states, turning the
  KIT-0034 manual scenario matrix into regression coverage. Minimum
  scenarios (from the retro's 8-state matrix): Gate 2 fallback PASS,
  no-review FAIL, unresolved-thread FAIL, CHANGES_REQUESTED FAIL, check-run
  source PASS, N3 precedence (completed non-success beats pending), gh-error
  FAIL (not PENDING), empty-fetch PENDING. The script itself stays shell +
  `gh` (KIT-0034 N2); only the harness is Python. Keep the harness pattern
  reusable — `sync_from_manifest.py`-style scripts could adopt it later.

- **F2 — pair task moves with coordination-metadata updates**: either
  `./scripts/core/project move|start|complete` rewrites known task paths
  (`details_link`, `handoff_file` values in
  `.kit/context/agent-handoffs.json`, and the `**Task**:` path line in
  `.kit/context/<TASK-ID>-HANDOFF-*.md`), or
  `.kit/context/workflows/COMMIT-PROTOCOL.md` documents the pairing as a
  mandatory same-commit step. Prefer the tooling fix if it stays simple
  (string rewrite of the numbered folder segment); CodeRabbit flags the
  drift within minutes on every status move, costing a bot round each time.

- **F3 — fix the two BugBot findings on `scripts/local/kit_markers.py`**
  (merged PR #58, both Medium, unresolved since 2026-06-27):
  1. *BEGIN-substring false positive abort*: during re-bootstrap, `merge`
     raises "malformed" when a region fails to parse but that region's exact
     BEGIN comment appears **anywhere** in the consumer file — a preserved
     region merely mentioning another region's marker in prose aborts
     `bootstrap-consumer.sh` under `set -e` instead of seeding from
     placeholders. Scope the malformed check to marker *lines*, not raw
     substring presence.
  2. *Whitespace marker clobber on re-bootstrap*: if a consumer's BEGIN
     marker drifts from the strict regex (extra spaces, minor edits) while
     customized body text remains, `extract_region` returns None, the
     malformed check doesn't fire, and `merge` silently replaces customized
     content with placeholder TODO text. Tolerate benign whitespace variance
     in the marker regex, or fail fast instead of clobbering.
  After the fix merges, reply to and resolve both PR #58 threads with a
  pointer to this task's PR.

### Non-Functional Requirements

- **N1**: F1 must not mutate real repo state — the stub `gh` and any git
  operations run against temp dirs with a cleaned environment (see the
  `GIT_DIR` gotcha in `TESTING-WORKFLOW.md`).
- **N2**: F3 keeps `kit_markers.py` stdlib-only and byte-preserving for
  well-formed regions (existing contract; its test suite must stay green).
- **N3**: New tests follow the F2/KIT-0034 rule: anything importing or
  reading `scripts/local/` is excluded from the consumer `tests/` rsync and
  module-skips when its dependency is absent.

## Acceptance Criteria

- [ ] Stub-`gh` pytest exercises the real `preflight-check.sh` across the
  8-state matrix and runs in CI
- [ ] Task-status moves no longer leave stale paths in
  `agent-handoffs.json`/handoff files (tooling), or COMMIT-PROTOCOL.md
  mandates the same-commit pairing (documentation) — one of the two, stated
  in the PR
- [ ] `kit_markers.py` no longer aborts on prose mentions of BEGIN markers
- [ ] `kit_markers.py` no longer silently replaces customized content when a
  marker has benign whitespace drift (fix or fail-fast, with test)
- [ ] Both PR #58 threads replied to and resolved with a pointer to the fix
- [ ] `pytest tests/test_kit_markers.py` and the full suite green; new tests
  excluded from consumer rsync per N3

## Test Plan

- F1: run the new harness locally and in CI; deliberately break a gate
  condition in a scratch branch to confirm the harness catches it.
- F3: add regression tests reproducing both BugBot scenarios (prose-mention
  consumer file; whitespace-drifted marker with customized body) before
  fixing.

## Notes

- Source: `.kit/context/retros/KIT-0034-retro.md` (Process Actions 1–3 plus
  the PR #58 triage item — planner triaged 2026-07-05: both findings are
  real latent bugs, hence F3 rather than a drive-by thread resolve).
- The retro's fourth action (specs must paste verified API output, not
  paraphrase bot signals) is a planner process rule, not implementation
  work — codified in the planner agents' Recurring Footguns and memory, not
  here.

## Evaluation (2026-07-05)

`arch-review-fast` (gemini-2.5-flash): **RESTRUCTURE_NEEDED** — split into
three tasks. Log:
`.adversarial/logs/KIT-0040-kit-0034-retro-followups--arch-review-fast.md`.
Planner disposition:

- **Declined (task split)**: for a single-operator kit, three tickets for
  one session of related retro follow-ups adds coordination overhead without
  value; the sibling bundles (KIT-0034 with five requirements, KIT-0035 with
  four) are scoped the same way and KIT-0034 shipped cleanly. All three
  items share one theme (KIT-0034 retro debt), one assignee, one review
  cycle.
- **Accepted (the valid kernel — F3 is independently urgent)**: encoded as
  PR sequencing instead of a split. **Implement F3 first**; if F1 or F2
  grows or stalls, ship F3 as its own PR immediately (it fixes a silent
  data-loss bug in consumer bootstraps) and let F1/F2 follow in a second
  PR. Per-requirement completion stays visible in the acceptance criteria
  either way.
