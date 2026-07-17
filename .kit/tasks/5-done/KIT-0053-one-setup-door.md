# KIT-0053: The one setup door (ADR-0027 P3)

**Status**: Done
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 5-7 hours (largest transformation task; 2-PR split pre-approved)
**Created**: 2026-07-15
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-ADR-0027 P3 (Accepted) — transformation task 4 of 6
**Related**: KIT-0048/0050 (shape+profile record and forcing this
formalizes), KIT-0046 (doctor, run at the door's end), KIT-0049
(sync stays the update path — untouched), P5+P7 (fill the resolution
seam this task leaves)

## Overview

Consolidate the kit's entrances into one command so a fresh agent
given a repo and one instruction cannot pick the wrong door. Current
door inventory (verified 2026-07-15): `scripts/optional/create-project.sh`
(clean new-project export), `scripts/local/bootstrap.sh`
(adopt-with-design-materials), `scripts/local/bootstrap-consumer.sh`
(kit-file sync/adopt — carries the shape/profile implementation),
plus the onboarding launcher and the docs that point at each. The door
becomes the single owner of the shape×profile legality matrix; the old
entrances become exec shims **on the same PR**, with their removal task
filed and pinned (ADR round-2 evaluation: unenforced deprecation is how
six doors happened).

## Requirements

### Functional Requirements

- **F1 — the door**: one kit-side entrance (suggested
  `scripts/local/bootstrap`; final name implementer's call, stated in
  the PR) with:
  - mode: `--new <target-dir>` (clean export path) or
    `--adopt <target-dir>` (existing-repo path); with design-material
    detection folded from bootstrap.sh's behavior where it applies;
  - `--shape single|planning`, `--profile python|none`,
    `--target-path/--target-github` (planning);
  - interactive prompts ONLY for unanswered questions (the ADR's
    wizard note: rich help, examples per combination);
  - orchestration: delegate to the existing engines (export / rsync /
    marker-merge), offer `install-evaluators`, offer venv setup when
    profile=python (setup-dev), and **finish every invocation with a
    `project doctor` run in the result** (P4 integration).
  - **Internal structure** *(accepted evaluation finding)*: one file,
    but composed of single-responsibility functions — resolve
    (the F5 chain), validate (the F2 matrix), orchestrate (engine
    calls) — each independently testable. No god-main; the test suite
    exercises resolve and validate without touching the filesystem.
- **F2 — matrix single-ownership**: the shape×profile legality table
  from the ADR lives in the door as data + validation: planning→none
  FORCED, illegal combos rejected with a message naming the legal
  pairs. The door RESOLVES; the existing bootstrap-consumer machinery
  keeps WRITING the kit-install record (one writer — the door must not
  become a second writer). Doctor keeps validating the record, never
  the matrix (ADR: single reader of the matrix is the door).
- **F3 — shims without shim-loops**: the three entrance FILENAMES
  become thin shims that map their historical flags onto door flags
  and `exec` the door. The implementations they contain move behind
  internal engine entry points the DOOR calls (rename in place or an
  internal-flag guard — implementer's call), so the call graph is
  strictly `shim → door → engine`, never `door → old entrance name`.
  **The same PR files the shim-removal task pinned to the next minor
  release** (ADR requirement, non-negotiable).
- **F4 — docs converge**: README, CLAUDE.md (Key Scripts table),
  the onboarding launcher/agent, and create-project agent point ONLY
  at the door; shims carry deprecation one-liners naming it.
- **F5 — the preset seam (P7 prep, NOT presets)**: implement argument
  resolution as an ordered chain — CLI flags → *(reserved preset
  layer, a stub that returns nothing)* → kit defaults → interactive
  prompt — with the seam documented in the door's header. P7 replaces
  the stub with the `~/.config/agentive-kit/preset` reader; this task
  ships the chain shape only. P5's bots-declaration is likewise NOT
  here.
- **F6 — door exit contract** (self-review item 8): `0` = install
  succeeded (doctor's verdict is REPORTED prominently, not encoded —
  a fresh repo with a doctor WARN is still a successful install);
  `1` = install failed; `2` = usage/illegal combination; document in
  the header.

### Non-Functional Requirements

- **N1 — characterization**: every historical invocation form of the
  three old entrances behaves identically through its shim (flag
  mapping pinned by tests; KIT-0048's characterization precedent).
- **N2**: system bash + python3 ≥ 3.11 + git + gh; no new deps.
- **N3**: the door is kit-side (runs from the kit clone against a
  target); it never lands in any sync tier or consumer rsync
  (scripts/local placement covers this — verify).
- **N4**: interactive prompts must be skippable in full by flags
  (agent sessions are non-TTY; every question has a flag).

## Acceptance Criteria

- [ ] `bootstrap --new` and `--adopt` scratch e2e for both shapes:
      one command → installed repo → doctor output shown, correct
      shape/profile recorded
- [ ] Illegal combos rejected (exit 2) naming legal pairs;
      planning→none forced
- [ ] All three old entrances are shims; historical flag forms pinned
      byte-identical (N1); call graph shim→door→engine verified
- [ ] Shim-removal task filed in the same PR, pinned to next minor
- [ ] Docs/launcher/agents reference only the door
- [ ] Resolution chain has the documented preset stub (P7 seam)
- [ ] Non-TTY: every prompt has a flag equivalent (N4 test)
- [ ] Door exit contract tested (0/1/2)

## Test Plan

- Characterize the three old entrances FIRST (their current flag
  surfaces on scratch targets) — the shim-mapping regression net.
- Door e2e per shape/profile cell of the matrix (legal cells pass,
  illegal cells exit 2).
- Non-TTY run with full flags (no prompt reached); non-TTY run with a
  missing answer (must fail with usage, not hang).

## Notes

- Source: KIT-ADR-0027 P3 incl. both evaluation rounds (matrix
  ownership; shims-not-deprecation-notes; enforced removal deadline)
  and the P7 amendment (resolution chain).
- 2-PR split pre-approved on the natural boundary: PR 1 = door +
  matrix + engines + doctor integration; PR 2 = shims + docs
  convergence + removal-task filing. If split, the removal task files
  with PR 2.
- Out of scope: presets themselves (P7), bots-declaration (P5),
  degraded modes, downstream migration (the post-P3 checkpoint COMES
  AFTER this lands), KIT-0051/0052.

## Evaluation (2026-07-15)

`arch-review-fast` (gemini-2.5-flash): **REVISION_SUGGESTED** — two
findings. Log:
`.adversarial/logs/KIT-0053-one-setup-door--arch-review-fast.md`.
Planner disposition:

- **Accepted — internal decomposition**: folded into F1 as
  single-responsibility functions (resolve / validate / orchestrate),
  independently testable. Right-sized form of the "sub-modules"
  suggestion.
- **Declined — externalize the matrix to YAML/JSON**: third appearance
  of this suggestion class (KIT-0048 deferred it here; ADR-0027/0025
  decline config machinery twice over). The matrix is six cells with
  one non-default rule; a constant data structure IN the door is
  already "data, not logic," with one owner and zero drift surface. A
  file format adds a reader and a failure mode for no flexibility this
  operator needs. Revisit trigger unchanged (a third shape or profile
  axis — ADR Consequences).
