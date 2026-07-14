# KIT-0041: Generalize the stub-gh harness to the remaining shell+gh scripts

**Status**: Backlog
**Priority**: low
**Assigned To**: unassigned
**Estimated Effort**: 2-3 hours
**Created**: 2026-07-05
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0040 (retro action #4) — the harness this generalizes
**Related**: KIT-0034 (where the stub-`gh` pattern was first proven manually)

## Overview

KIT-0040 F1 built a pytest harness for `preflight-check.sh`: a PATH-stubbed
`gh` serving canned payloads keyed by argv shape, plus stubbed `sleep`
(instant poll loops) and `dispatch` (no event leakage), a cleaned git
environment, and module-scoped fixtures (1.8 s for the whole module). The
pattern is documented in `tests/test_preflight_check.py`'s docstring.

`verify-ci.sh`, `check-bots.sh`, and `wait-for-bots.sh` remain untested
shell+gh scripts of the same shape. Lift the stub machinery into a shared
`tests/` helper and cover at least `verify-ci.sh`.

## Goal

1. Extract the stub-`gh`/`sleep`/`dispatch` fixture machinery from
   `tests/test_preflight_check.py` into a shared helper (e.g.
   `tests/gh_stub.py` or conftest fixtures), keeping
   `test_preflight_check.py` green through the refactor.
2. Add scenario coverage for `verify-ci.sh` (minimum: all-green PASS,
   failed-run FAIL, no-runs-yet, and the PR-event workflow gap noted in
   REVIEW-INSIGHTS.md "CI Verification").
3. `check-bots.sh` / `wait-for-bots.sh` coverage if cheap; otherwise note
   what a follow-up needs. Model canned payloads on the correct API surface
   per bot (CodeRabbit = commit statuses, BugBot = check-runs).

## Acceptance Criteria

- [ ] Shared stub helper exists; `test_preflight_check.py` uses it and stays
      green with no scenario changes
- [ ] `verify-ci.sh` has stub-based scenario coverage running in CI
- [ ] Harness runtime stays inside the pre-commit fast-hook budget, or new
      modules carry a `slow` marker with the fast-hook excluding them
- [ ] Scripts themselves unchanged (harness-only task)

## Notes

- Source: `.kit/context/retros/KIT-0040-retro.md` (Process Action #4).
- Post-v0.8.0 candidate — valuable but not release-blocking; the release's
  critical gate script (`preflight-check.sh`) is already covered.
- **Scope addition (2026-07-14, KIT-0046 retro)**: also absorb
  `test_doctor.py`'s `_restricted_bin` PATH-fixture helper into the
  shared harness — third instance of the stub-a-binary pattern (fake
  `gh`, no-op `sleep`/`dispatch`, restricted PATH with symlinked
  `awk`). Consolidate all of them behind one helper module.
