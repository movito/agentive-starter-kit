# KIT-0042: Preflight support for task bundles (Gates 5/6 exact-name match)

**Status**: Todo
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 1-2 hours
**Created**: 2026-07-05
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0037/38/39 bundle — surfaced in its retro
**Related**: KIT-0036 (first bundled arc), KIT-0034/KIT-0040 (preflight
hardening lineage; KIT-0040's stub-gh harness covers new gate logic)

## Overview

Task bundles are now an established pattern (KIT-0036's two-PR arc, the
KIT-0037/38/39 single-PR bundle), but `preflight-check.sh` assumes one task
ID per PR: Gate 6 does an exact-name find for `<TASK-ID>-REVIEW-STARTER.md`
(`preflight-check.sh:487`), and Gate 5 keys evaluator artifacts to a single
task ID the same way. A bundled PR fails both gates until the implementer
discovers — by failing the gate — that they must rename artifacts to the
lead task and create per-task pointer files. The KIT-0037/38/39 session's
pointer files are the reference shape.

## Requirements

- **F1 — pick one mechanism and implement it**:
  - *(a) Gate tolerance*: loosen Gates 5/6 to a glob that tolerates combined
    names (e.g. `<TASK-ID>*REVIEW-STARTER.md` matches
    `KIT-0037-38-39-REVIEW-STARTER.md` when checking KIT-0038 requires the
    check to scan for the task ID *within* starter filenames), OR
  - *(b) Convention*: codify the lead-task + per-task-pointer-files pattern
    in the review-handoff skill (`.kit/skills/review-handoff/`) so the next
    feature-developer does it up front instead of at Phase 8.
  Option (b) is cheaper and keeps the gates strict; option (a) removes the
  manual step. Implementer's choice — state the reasoning in the PR. If (a),
  verify the glob cannot false-positive across unrelated tasks sharing a
  prefix (KIT-0004 vs KIT-0040 — see the `(?!-?\w)` name-terminator lesson
  from KIT-0040).
- **F2 — regression coverage**: if gate logic changes, extend the KIT-0040
  stub-`gh` harness (`tests/test_preflight_check.py`) with a bundle
  scenario; if convention-only, no test needed.

## Acceptance Criteria

- [ ] A bundled PR passes Gates 5/6 either natively (glob) or by following a
  documented up-front convention — no more discover-by-failing
- [ ] The chosen mechanism and reasoning stated in the PR
- [ ] Gate changes (if any) covered in `tests/test_preflight_check.py`;
  prefix false-positives explicitly tested
- [ ] Reference: the KIT-0037/38/39 pointer files named as the example shape

## Notes

- Source: `.kit/context/retros/KIT-0037-38-39-retro.md` (Should Change #1 /
  Process Action). v0.8.0 candidate — sequenced after KIT-0035.
