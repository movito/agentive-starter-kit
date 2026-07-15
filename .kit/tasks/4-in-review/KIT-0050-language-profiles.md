# KIT-0050: Language profiles — the check hook separates kit from toolchain (ADR-0027 P1)

**Status**: In Review
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 4-6 hours
**Created**: 2026-07-15
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-ADR-0027 P1 (Accepted) — transformation task 3 of 6
**Related**: KIT-0048 (shape record + doctor declarations this
extends), KIT-0049 (manifest intersection — profile files ride the
same rules), KIT-0035 F1 (ci-check Black warning, absorbed into the
python profile content)

## Overview

Finish unwinding the Python presumption: the kit's machinery stays
Python (invisible plumbing), but the *project's* toolchain becomes a
replaceable profile behind one project-owned hook. `ci-check.sh`
becomes a thin dispatcher; the current Python gauntlet becomes the
seeded default hook content; a JS adopter replaces one file; `none`
covers docs-only repos. Preflight needs nothing — it is already
shell + `gh`.

**Profile model (v1)**: `python` (default for `single` shape —
byte-identical to today), `none` (no-op hook with a clear message;
FORCED for `planning` shape per the ADR matrix), and *custom* (the
adopter edits the seeded hook following the contract — the kit ships
no toolchains it doesn't itself use; "js profile" = the contract plus
a two-line hook the adopter writes).

## Requirements

### Functional Requirements

- **F1 — dispatcher**: `ci-check.sh` executes
  `scripts/local/checks.sh --mode ci` when the hook exists; when it
  does NOT exist, it falls back to its current built-in Python gauntlet
  **byte-identically** (N1 — existing consumers unaffected until they
  opt in). The dispatcher owns nothing else: no profile logic, no
  interpretation of hook output beyond the exit code.
- **F2 — the hook micro-contract** (ADR-0027 P1, verbatim semantics):
  accepts `--mode ci|local`; exits `0` (pass) or `1` (fail) only;
  human-readable diagnostics to stdout; invoked from the repo root
  with no other environment guarantees; nothing else passed through.
  The contract lives as a comment header in every seeded hook and one
  paragraph in the workflow docs — a paragraph, never a schema (N3).
- **F3 — seeded profiles**: bootstrap gains `--profile python|none`
  (single shape only; default `python`; `planning` forces `none` — the
  P3 matrix pairing, hard-coded as in KIT-0048):
  - `python` seeds `scripts/local/checks.sh` with the current gauntlet
    content (Black + venv-drift warning from KIT-0035 F1, isort,
    flake8, pattern_lint, pytest, coverage) — the kit's own tested
    default, moved not rewritten;
  - `none` seeds a no-op hook that says so loudly and exits 0.
- **F4 — profile record**: the `kit-install` region gains a
  `profile:` line (writer: bootstrap; reader: the `_doctor_shape()`
  family — extend to return shape+profile). Absent profile = `python`
  for single, `none` for planning (back-compat). Malformed = the
  KIT-0048 fail-loud pattern (full doctor set + FAIL line).
- **F5 — doctor profile scoping**: the three toolchain checks
  (venv, skew, Black) move from `# shapes: single` to profile
  scoping — active only when the effective profile is `python`. Reuse
  the KIT-0048 header-declaration mechanism (e.g.
  `# profiles: python`); driver stays declaration-driven, no if/else.
- **F6 — CLAUDE.md Project Rules as a KIT-LOCAL region**: wrap the
  consumer-facing "Project Rules" section in
  `<!-- BEGIN/END KIT-LOCAL: project-rules -->`; bootstrap seeds it
  per profile (python = current rules text; none = a minimal
  conventions note). The kit's own CLAUDE.md gets the markers too so
  re-bootstrap machinery stays uniform (content unchanged).

### Non-Functional Requirements

- **N1**: hook-absent behavior is byte-identical to today's
  `ci-check.sh` (characterization test), and `--profile python`
  seeding produces a hook whose `--mode ci` output matches the
  built-in gauntlet's on the same tree.
- **N2**: pre-commit variants beyond the existing planning one are OUT
  of scope — the pre-commit/profile coupling is a P3-era question;
  note it, don't build it.
- **N3**: no schema, no config file, no profile registry — the hook is
  the interface; profiles are seed content.
- **N4**: `scripts/local/checks.sh` is consumer-owned after seeding
  (never overwritten by sync — verify it is not in any synced tier;
  it rides KIT-0049's manifest-intersection rules naturally).

## Acceptance Criteria

- [ ] `ci-check.sh` with no hook: byte-identical to current behavior
      (characterization)
- [ ] `--profile python` scratch consumer: seeded hook passes the
      contract, `ci-check.sh` dispatches to it, output equivalent to
      built-in
- [ ] `--profile none` scratch consumer: loud no-op, exit 0; planning
      shape forces it
- [ ] Doctor: toolchain checks run under python profile, SKIP
      (declaration-driven) under none/planning; malformed profile =
      fail-loud
- [ ] `kit-install` region carries `profile:`; reader extended;
      back-compat defaults tested
- [ ] Project Rules region marker-wrapped in kit + seeded per profile;
      re-bootstrap preserves consumer edits (kit_markers round-trip)
- [ ] Hook never overwritten by `project sync` (test rides KIT-0049
      suite)
- [ ] Contract paragraph in the workflow docs; header template in both
      seeds

## Test Plan

- Characterization of `ci-check.sh` first (N1 net, KIT-0048
  precedent).
- Scratch consumers per profile (mktemp e2e, both shapes).
- Contract conformance: run each seeded hook with `--mode ci`,
  `--mode local`, bogus mode (must fail with usage, not silently
  pass).
- Doctor declaration tests extend `test_doctor.py`'s KIT-0048 shape
  cases.

## Notes

- Source: KIT-ADR-0027 P1 (incl. the hook micro-contract added at
  evaluation) + P3 matrix (single×{python,none} legal here; js = custom
  hook, not a shipped pack).
- Out of scope: the one door (P3 — `--profile` on bootstrap-consumer
  is the interim entrance), presets (P7), pre-commit variants (N2),
  shipping non-Python toolchain packs, downstream migration.

## Evaluation (2026-07-15)

`arch-review-fast` (gemini-2.5-flash): **APPROVED — zero findings**
("Architecture is sound"). First clean approve of the transformation
arc; the ADR's pre-decided hook contract and the KIT-0048/0049
mechanisms this extends left nothing undecided. Log:
`.adversarial/logs/KIT-0050-language-profiles--arch-review-fast.md`.
Zero evaluator working-tree mutations.
