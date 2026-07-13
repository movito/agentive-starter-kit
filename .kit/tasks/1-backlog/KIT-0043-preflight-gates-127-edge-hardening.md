# KIT-0043: Preflight Gates 1/2/7 edge-case hardening (recurring evaluator findings)

**Status**: Backlog
**Priority**: low-medium
**Assigned To**: unassigned
**Estimated Effort**: 2-3 hours
**Created**: 2026-07-14
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0042 (bundle-aware Gates 5/6) — these findings were
declined there as out of scope
**Related**: KIT-0034 (landed Gates 1–4 logic), KIT-0040 (stub-`gh`
harness these fixes would extend), KIT-0041 (harness generalization)

## Overview

Across KIT-0042's evaluator rounds, two evaluators (o3 and
code-reviewer-fast-v2) independently and repeatedly flagged the same set
of latent edge cases in `scripts/core/preflight-check.sh` — three runs,
same four findings. Each was correctly declined as out of scope for
KIT-0042 (its surface was Gates 5/6 only), but the convergence and
repetition are signal: these live only in decline tables today
(`.kit/context/reviews/KIT-0042-evaluator-review.md`) and deserve one
tracked pass. Gate 7's boundary-less wildcard is the same bug-class
KIT-0042 just pinned tests for on Gates 5/6.

## Requirements

- **F1 — Gate 1 run-list truncation**: `gh run list --limit 10` silently
  drops runs beyond 10; a dropped failing run yields a false PASS on a
  matrix-heavy push. Either raise the limit meaningfully, page until
  exhausted, or filter server-side by head SHA. Verify against the real
  `gh run list` flag surface before choosing (verify-before-believing —
  paste the checked command in the PR).
- **F2 — Gate 1 unknown statuses read as FAIL**: statuses other than
  `completed`/`in_progress`/`queued` (e.g. `waiting`, `requested`,
  `pending`, `action_required`) fall into the failure branch. Non-terminal
  unknowns should count toward PENDING (KIT-0034's pending-vs-failed
  distinction), not FAIL. Enumerate GitHub's current status values from
  the API docs rather than guessing.
- **F3 — Gate 7 prefix boundary**: `find ... -name "${TASK_ID}*"` has no
  separator after the ID (`KIT-4*` matches `KIT-40-...`). Nil risk with
  fixed-width KIT-NNNN IDs today, but it is the exact bug-class KIT-0040
  fixed in kit_markers and KIT-0042 pinned tests for on Gates 5/6. Add
  the boundary (`${TASK_ID}-*` should suffice — task files are named
  `<ID>-slug.md`) plus a pinning test mirroring
  `test_prefix_is_not_a_match_boundary_violation`.
- **F4 — Gate 2 fallback mixed commit-status contexts** *(verify first)*:
  o3 claims a mixed success/failure pair of CodeRabbit contexts can slip
  the fallback. The claim is convoluted and was never verified — F4's
  first step is to reproduce it in the stub-`gh` harness; if it does not
  reproduce, record the decline with the repro and drop the fix.
- **F5 — regression coverage**: every accepted fix gets a stub-`gh`
  harness case in `tests/test_preflight_check.py` (multi-run payloads for
  F1, unknown-status payloads for F2, fixture-collision case for F3).

## Acceptance Criteria

- [ ] Gate 1 cannot false-PASS from run-list truncation (or the chosen
      limit is justified against real repo run counts in the PR)
- [ ] Non-terminal unknown CI statuses produce PENDING, not FAIL
- [ ] Gate 7 has a boundary-safe match with a pinning test
- [ ] F4 reproduced-or-declined with harness evidence
- [ ] All gate changes covered in `tests/test_preflight_check.py`;
      `GATE:N:Name:VERDICT:` format unchanged
- [ ] The KIT-0042 decline-table entries updated to point here

## Notes

- Source: `.kit/context/reviews/KIT-0042-evaluator-review.md` (rounds 1–2
  decline tables) — o3 + fast-v2 convergent findings, three runs.
- Also parked there, lowest value: `head -1` on multi-match `find` output
  is order-arbitrary. Only act on it if F3's edit touches the same lines.
- Operator context (2026-07-14): CodeRabbit prepaid credits exhausted —
  Gate 2's *bot availability* is a separate operational issue, not this
  task; this task is only the fallback-logic edge case (F4).
