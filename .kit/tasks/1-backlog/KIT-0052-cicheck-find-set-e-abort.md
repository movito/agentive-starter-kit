# KIT-0052: Fix the `find`-under-`set -e` silent abort in ci-check + python seed

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 1-2 hours
**Created**: 2026-07-15
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0050 (retro Surprising #3 / Should-Change #4 — found by
the characterization harness, deliberately NOT fixed there to preserve
N1 byte-identity)

## Overview

`PY_FILES=$(find scripts/ tests/ ...)` under `set -e` (stderr
discarded) makes `ci-check.sh` — and the KIT-0050 python seed, which
preserved it move-not-rewrite — **die silently mid-run** when either
directory is absent. Latent in every consumer; a docs-only or
partially-scaffolded repo gets a truncated check run that looks like a
pass path.

## Requirements

- Fix BOTH `ci-check.sh`'s built-in gauntlet and
  `checks-python.sh` (the seed) **in one commit**, re-pinning the
  characterization goldens in that same commit — the equivalence test
  (`TestPythonSeedEquivalence`) must never straddle a state where one
  side is fixed and the other isn't.
- Fix shape: missing dir → explicit named notice (the masking class:
  say what was skipped) and continue or fail loudly — never a silent
  truncated run. Decide continue-vs-fail against the `none`-profile
  boundary (a repo with no `tests/` arguably wants the `none` profile;
  the notice should say so).
- Seed version bump + core scripts version per convention.

## Acceptance Criteria

- [ ] Missing `scripts/` or `tests/` produces a named notice, never a
      silent mid-run abort (test with scratch dirs)
- [ ] Built-in and seed fixed in ONE commit with goldens re-pinned
      (git history shows no straddle state)
- [ ] Equivalence test green before and after

## Notes

- Source: `.kit/context/retros/KIT-0050-retro.md` Surprising #3.
- **Parked here (planner, 2026-07-15) — the unresolved evaluator
  auto-cancel contradiction**: KIT-0044 verified `echo y |` satisfies
  the adversarial CLI's large-input confirm in non-TTY; KIT-0050
  observed all three trio runs auto-cancel with exit 0 on the same
  1.0.1. The KIT-0050 explanation (an `ADVERSARIAL_UNATTENDED` flag)
  was disproven (flag exists nowhere; 1.0.1 is latest). While in this
  task's neighborhood, if convenient: reproduce a >17k-token non-TTY
  run with and without the pipe and record actual behavior + exit
  codes in the review record. Do not change any guidance without the
  repro.
