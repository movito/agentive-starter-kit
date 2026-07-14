# KIT-0048: Planning-repo shape — install the kit without a toolchain (ADR-0027 P2)

**Status**: In Review
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 4-6 hours
**Created**: 2026-07-14
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-ADR-0027 P2 (Accepted) — transformation task 2 of 6
**Absorbs**: KIT-0027 (first-class cross-repo support) — its intent
lands here; its `current-state.json` mechanism is redirected (see F2)
**Related**: KIT-0046 (doctor's `TODO(P2)` seam, filled here),
KIT-0033 (marker-merge machinery this reuses), KIT-ADR-0024 (topology
conventions — unchanged by this task)

## Overview

Make the planning-repo shape a first-class installation: a repo that
coordinates a target product repo gets `.kit/`, agents, commands, and
the lifecycle/gate machinery — and **no Python project toolchain** (no
pyproject, no tests/, no venv requirement, no Black/pytest gauntlet).
The target repo receives nothing, ever. This is the ADR's "earliest
new-capability point": after this task, adopting the kit for a
non-Python product = create a sibling planning repo in minutes.

Verified runtime fact (planner, 2026-07-14): `scripts/core/project`
runs on system `python3 ≥ 3.11` — stdlib throughout (`tomllib` is
stdlib as of 3.11); the `gql`/`dotenv` imports live only in the
optional Linear-sync path, which already degrades gracefully. The
planning shape therefore needs no venv for the lifecycle machinery.

## Requirements

### Functional Requirements

- **F1 — `bootstrap-consumer.sh --shape planning`** (default remains
  `single` = exactly current behavior; ADR rollout promise: existing
  consumers unaffected). The planning install ships:
  - `.kit/` skeleton (tasks folders, context, templates, workflows) —
    the existing scaffold path;
  - agents (marker-merged, as today) and `.claude/commands/`;
  - lifecycle + gate machinery: `project`, `preflight-check.sh`,
    `doctor` + `doctor.d/`, `kit_markers.py`, `gh-review-helper.sh`,
    `prepare-review-input.sh`, `new-worktree.sh`;
  - `.adversarial/` config + evaluator install offer (ADR open
    question resolved YES: planners run spec evaluations — this is the
    planning shape's one optional-services dependency, and P5's
    degraded mode will soften it later).
  It must NOT ship: `pyproject.toml`, `tests/`, `conftest.py`,
  `ci-check.sh`'s Python gauntlet, `pattern_lint.py`, or any venv
  bootstrap. Derive the two file-sets explicitly in the script (an
  enumerated list, not a glob — the KIT-0044 provisioning lesson).
  *Scalability note (from evaluation)*: the enumerated list is
  right-sized for exactly two shapes; if a third shape ever appears,
  generalizing to a declarative set belongs to P3's door — do not
  build that machinery here.
- **F2 — the shape record**: the planning install writes a
  `<!-- BEGIN/END KIT-LOCAL: kit-install -->` region into the
  consumer's CLAUDE.md via `kit_markers.py` recording
  `shape: planning` and the target-repo pointer (path + github). This
  absorbs KIT-0027's `target_repo` intent but **redirects the
  mechanism**: runtime-read CLAUDE.md region per ADR-0025/0027, not a
  `current-state.json` field. The existing `## Target Repository`
  section and its `grep` detection convention (KIT-ADR-0024) are
  UNCHANGED — agents keep reading what they read today; the region is
  the machine-written record, seeded to match.
- **F3 — doctor per-shape inclusion**: fill KIT-0046's `TODO(P2)`
  seam — **via check-level declarations, not driver if/else** (accepted
  evaluation finding): each `doctor.d/` check declares its applicable
  shapes in a header line (e.g. `# shapes: single` /
  `# shapes: single planning`); the driver reads the shape record once
  and includes/SKIPs per declaration. This is the cheapest form of the
  suggested registry and keeps the driver shape-agnostic. Semantics:
  absent record = `single` (full set, back-compat);
  **malformed/unknown shape value = run the FULL check set AND emit
  `DOCTOR:shape-record:FAIL:<detail>`** — fail loud while staying
  maximally diagnostic, never silently fall back (accepted evaluation
  finding). Planning shape: venv/skew/Black checks SKIP with shape
  note; gh, env-keys, evaluators, plugin-source, core.bare stay
  active.
- **F4 — a planning-appropriate pre-commit**: ship a minimal
  `.pre-commit-config.yaml` variant for planning installs —
  whitespace, end-of-file, `validate-task-status` (task hygiene is
  exactly what a planning repo needs) — and none of the Python hooks.
  Implementer latitude on mechanism (separate template vs generated).
- **F5 — KIT-0027 disposition**: annotate KIT-0027's spec as absorbed
  here (intent) with the mechanism redirect recorded, and retire it
  from the backlog (superseded, not deleted — same treatment as prior
  supersessions).

### Non-Functional Requirements

- **N1**: `--shape single` (and no flag) is byte-identical to today's
  behavior — zero change for existing consumers.
- **N2**: everything the planning shape installs must run on system
  `python3 ≥ 3.11` + `git` + `gh` — no venv, no pip installs (the
  evaluator library being the explicit, offered-not-required
  exception).
- **N3**: the target repo is never written to by any part of this
  task's machinery.
- **N4**: shape detection must be cheap and runtime-read (one
  `kit_markers.py` extract) — no caching layer, no config file.

## Acceptance Criteria

- [ ] Scratch e2e (mktemp, KIT-0033 pattern): `bootstrap-consumer.sh
      --shape planning` produces a repo where `project start/move/complete`,
      `preflight-check.sh --task X --pr N` (against a real or stubbed
      PR), and `project doctor` all run green on system python3 — with
      NO pyproject/tests/venv present
- [ ] Doctor in the scratch planning repo: toolchain checks SKIP with
      shape note; gh/env/evaluators/core.bare checks run
- [ ] `--shape single` and flagless runs byte-identical to current
      output (characterization check)
- [ ] CLAUDE.md `kit-install` region written with shape + target
      pointer; `## Target Repository` convention untouched
- [ ] KIT-0027 annotated + retired as absorbed
- [ ] New tests follow the consumer-rsync exclusion rule where they
      read `scripts/local/` (self-review item 7)
- [ ] Doctor run from BOTH shapes pasted in the PR description

## Test Plan

- Characterization first: capture current flagless bootstrap output on
  a scratch consumer, assert `--shape single` matches (N1).
- Planning e2e per acceptance criteria; deliberately break one
  planning-shape assumption (e.g. add a pyproject) and confirm doctor
  still behaves sanely (it diagnoses, never assumes).
- `tests/test_bootstrap_consumer.py` extensions for the file-set
  lists; `tests/test_doctor.py` extension for shape-based inclusion.

## Notes

- Source: KIT-ADR-0027 P2 + rollout table ("earliest new-capability
  point"). The shape × profile matrix (P3) forces `planning → none`;
  this task hard-codes that pairing rather than building profile
  selection — P1/P3 will generalize it.
- Out of scope: language profiles (P1), the one door (P3 — the
  `--shape` flag on bootstrap-consumer is the interim entrance and
  becomes a shim argument later), presets (P7), migrating any existing
  planning repo (ID2-style repos migrate at the post-P3 checkpoint).

## Evaluation (2026-07-14)

`arch-review-fast` (gemini-2.5-flash): **REVISION_SUGGESTED** — three
findings, design "fundamentally sound". Log:
`.adversarial/logs/KIT-0048-planning-repo-shape--arch-review-fast.md`.
Planner disposition:

- **Accepted — doctor shape-selection via check-level declarations**
  (`# shapes:` header per check) instead of driver if/else; folded into
  F3. The cheapest registry form, and it keeps the driver shape-blind.
- **Accepted — malformed shape values fail loud**: full check set +
  `DOCTOR:shape-record:FAIL`; folded into F3. Absent ≠ malformed.
- **Deferred — declarative provisioning file-sets**: right-sized as an
  enumerated list at two shapes; generalization is P3's remit if a
  third shape appears (noted in F1). Building it now would be the
  config machinery ADR-0025/0027 decline.
