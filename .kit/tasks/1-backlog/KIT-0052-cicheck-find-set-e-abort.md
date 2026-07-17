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
- ~~Parked contradiction~~ **RESOLVED (planner empirical matrix,
  2026-07-17)**: three adversarial installs, all "1.0.1" — the
  operator's editable dev build (`/opt/homebrew/bin`) implements
  `ADVERSARIAL_UNATTENDED` and auto-cancels exit 0 without it; PyPI
  builds (.venv, Framework) use plain `input()` where `echo y |`
  works. Guidance updated everywhere to the belt-and-braces
  `echo y | ADVERSARIAL_UNATTENDED=1 …` form
  (prepare-review-input.sh 1.5.2, code-review-evaluator skill). No
  repro needed in this task anymore; the doctor blind spot went to
  KIT-0055.
