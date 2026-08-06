# KIT-0089: Test-suite modularity — stop the monolith test files from growing, split them once during packaging

**Status**: Backlog
**Priority**: medium (guardrail half is cheap and immediate; split half is deliberately deferred to the ADR-0028 migration so the reorganization happens once)
**Type**: Testing / infrastructure
**Estimated Effort**: guardrail 0.5 day; split rides the packaging extraction
**Created**: 2026-08-05
**Source**: operator, PR #106 review — "our test_project_script is more than 2000 lines long. This is not maintainable."

## Overview

Measured on main, 2026-08-05: `tests/test_doctor.py` 1973 lines,
`tests/test_setup_door.py` 1537, `tests/test_project_script.py` 1334
(PR #106 pushes it past 2000); `tests/` total 12,562 lines across 11
files. Root cause: **test files mirror production files, and the
production files are single-file monoliths** — `scripts/core/project`
is 2564 lines carrying ~20 subcommands, so every new subcommand's tests
land in the one file named after the one script.

The monolith shape is itself a copy-distribution artifact (one file =
one rsync target). KIT-ADR-0028 retires that constraint: the scripts
become a real Python package with modules. The test split must
therefore happen **as part of that extraction, not before it** — a
pre-migration reorganization would be redone weeks later (two passes
over 12k lines instead of one).

## Requirements

- **F1 — size guardrail, now (standalone, does not wait for the
  migration).** A machine-enforced check — pattern-lint rule or
  pre-commit hook, implementer's choice with rationale — that WARNs
  when any `tests/*.py` or `scripts/**` file exceeds a soft ceiling
  (proposed: 800 lines) and FAILs above a hard one (proposed: 1500).
  Existing over-limit files are grandfathered via an explicit allowlist
  **with a shrink-only rule: the allowlist entry records the file's
  current line count, and the check fails if the file GROWS beyond it**
  — so the debt can only shrink, and the allowlist retires with the
  split. Prose rules don't propagate (KIT-0088 lesson); this must be a
  check, not a paragraph.
- **F2 — shared fixtures to `conftest.py`, now.** Much of the monolith
  test files is repeated fixture scaffolding (repo builders, the
  `sourced()` shell harness from KIT-0084, stub binaries). Extracting
  shared fixtures into `tests/conftest.py` (or `tests/fixtures/`
  modules) is cheap, makes any later split mechanical, and survives the
  packaging migration unchanged.
- **F3 — the split itself, DURING ADR-0028 phase 1.** When
  `scripts/core/project` becomes package modules
  (lifecycle / doctor / evaluators / sync / coordination), tests split
  with them: one test module per package module, e.g.
  `tests/doctor/test_<check>.py` per doctor.d check rather than one
  1973-line `test_doctor.py`. The packaging task's spec must name this
  as an acceptance criterion — record the pointer there when that spec
  is written, and close F3 here by reference.
- **F4 — TESTING-WORKFLOW.md** gains the placement rule (new tests go
  in the module-mirroring file; a file at its ceiling is split in the
  same PR) — one paragraph, pointing at the F1 check as the enforcer.

## Acceptance Criteria

- [ ] The size check runs in pre-commit and CI; a file crossing its
      ceiling fails loudly with the split instruction
- [ ] Grandfathered files cannot grow (shrink-only allowlist verified
      by a test)
- [ ] Shared fixtures live in conftest/fixtures modules; at least the
      two largest test files consume them instead of local copies
- [ ] The ADR-0028 packaging spec (when written) carries the
      tests-split-with-modules criterion, referenced from here
- [ ] TESTING-WORKFLOW.md states the placement rule

## Out of Scope

- Splitting `scripts/core/project` itself before the packaging
  migration (that IS the migration)
- Rewriting existing tests beyond fixture extraction
- Coverage changes

## Notes

- The proposed ceilings (800/1500) are starting points — the
  implementer may adjust with one line of rationale; what is not
  negotiable is that the limit is machine-enforced and the allowlist
  is shrink-only.
