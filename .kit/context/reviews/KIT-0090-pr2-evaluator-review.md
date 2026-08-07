# KIT-0090 PR 2 — Evaluator Review Record

**PR**: #109 (stacked on #108) — doctor migration
**Date**: 2026-08-06
**Ordering**: trio run BEFORE PR open

## Rounds

- **code-reviewer-fast**: CONCERNS — .env quote-handling robustness
  (pre-existing check behavior, extraction-neutral: declined),
  `_check_declared` regex strictness (legacy-identical, pinned by
  tests: declined), `_kit_doctor`-absent path untested (superseded by
  the inline-fallback design below).
- **code-reviewer (o3)**: FAIL — packaged checks may ship without
  exec bits in pip/sdist installs and the driver FAILed them.
  **Taken** (adf5b96): suffix-interpreter fallback for the packaged
  checks dir only; repo-local `doctor.d`/`--dir=` keep the strict
  pinned contract. Secondary items were repeats from PR 1 dispositions.

## Post-open CI finding (the real catch of this PR)

The dispatched CI run on adf5b96 FAILED: door E2E tests bootstrap
fresh consumer targets whose copied script delegated `doctor` to a
package they don't carry. Fix: the script keeps its inline driver as a
FALLBACK when no package is importable (package canonical; recorded
duplication, dies with the script in phase 4). Lesson recorded for the
retro: the pre-commit fast hook deselects the door E2E tests — run the
FULL suite after any script-delegation change.
