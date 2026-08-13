# KIT-0107: Remove the bootstrap shim (and the materials branch with it)

**Status**: Backlog
**Priority**: medium — **pinned to the next minor kit release (0.10.0)**;
an unenforced "one release later" is how six doors became six
(KIT-ADR-0027 P3)
**Type**: Deprecation removal
**Estimated Effort**: 2-3 hours
**Created**: 2026-08-13
**Source**: KIT-0104 F3 (KIT-ADR-0030) — the door moved into the
agentive-kit package as `agentive new` / `agentive adopt`;
`scripts/local/bootstrap` stayed behind as a thin exec shim for one
minor release, printing its own removal notice pointing at this task.

## Overview

`scripts/local/bootstrap` is an exec shim over
`python3 -m agentive_kit.cli new|adopt` (it prefers the checkout's own
`packages/agentive-kit/src`). It carries exactly one piece of behavior
of its own: the `--adopt <dir> --design-materials` branch, which still
drives `scripts/local/engine-materials.sh` directly because the
interactive materials flow cannot ship as package data. Both die
together here.

## Requirements

- **F1 — delete the shim.** `scripts/local/bootstrap` goes away; the
  packaged verbs are the only door. Add the path to
  `tests/test_entrance_shims.py::TestOldEntrancesRemoved` so a
  resurrected copy hard-fails.
- **F2 — the materials flow retires with it.** By then the
  `project-intake` agent (KIT-0105, blocked on KIT-0104) is the
  materials successor. Remove `engine-materials.sh` + its tests
  (`tests/test_engine_materials.py`, the materials E2E in
  `test_entrance_shims.py`) or, if KIT-0105 has not landed, STOP and
  re-sequence — the kit must not lose its only materials path.
- **F3 — the packaged door's `--design-materials` refusal drops its
  "while the shim lasts" pointer** (`agentive_kit/door/__init__.py`)
  and points only at project-intake.
- **F4 — test/module sweep.** `tests/test_setup_door.py` and
  `tests/test_bootstrap_shapes.py` pin the SHIM contract — they retire
  with it (their packaged coverage already lives in
  `tests/agentive_kit/test_door_*`). `tests/test_scaffold_acceptance.py`
  re-anchors `run_door` onto the packaged CLI. Module-skip guards that
  key on the bootstrap path (`test_door_data_sync.py`,
  `test_bots_conformance.py`, `test_project_script.py`,
  `test_entrance_shims.py`) need a new kit-repo sentinel.
- **F5 — prose sweep by class**: every surface naming
  `scripts/local/bootstrap` as a live entrance (CLAUDE.md Key Scripts
  table, docs/, `.claude/commands/new-project.md`, agent files) moves
  to the packaged verbs. Grep the class, not the instances.

## Acceptance

- [ ] `scripts/local/bootstrap` and `scripts/local/engine-materials.sh`
      are gone; `TestOldEntrancesRemoved` covers both
- [ ] No live surface instructs running `scripts/local/bootstrap`
- [ ] Full suite green on a tree with no shim

## Notes

- Pinned pair: KIT-0108 (engine consolidation) shares the 0.10.0 pin;
  landing them together deletes the `door/engines/` duplication and the
  shim in one release.
