# KIT-0108: Consolidate the door engines into the package

**Status**: Backlog
**Priority**: medium — **pinned to the next minor kit release (0.10.0)**,
the same pin as KIT-0107 (the arch-review-fast disposition on KIT-0104:
the engines-as-data interim needs a filed exit, and a missed pin is the
parent ADR's revisit trigger)
**Type**: Architecture / packaging
**Estimated Effort**: 1-2 days
**Created**: 2026-08-13
**Source**: KIT-0104 F2 (KIT-ADR-0030) — the port shipped the Python
front as the matrix's single owner while `engine-scaffold.sh` and
`engine-consumer.sh` ride along as packaged data, byte-pinned to their
kit-tree twins by `tests/test_door_data_sync.py`. That duplication is
an interim, and this task is its filed exit.

## Overview

Today every engine edit must land in two homes in the same commit
(`scripts/local/engine-*.sh` ↔
`packages/agentive-kit/src/agentive_kit/door/engines/`), and the data
store under `door/data/` byte-mirrors ~15 kit-tree sources. The sync
guard makes the duplication safe, not cheap. Consolidate: the engines'
behavior moves into `agentive_kit.door` (or the engines become
package-only), the kit tree stops carrying a second copy, and the sync
guard retires with the duplication it guarded.

## Requirements

- **F1 — one home per engine.** Either port the two engines' behavior
  to Python inside `agentive_kit.door` (preferred — ends the bash 3.2 /
  BSD-userland constraint for good) or make the packaged copies the
  ONLY copies with the kit tree consuming them from the package. No
  byte-pinned twins either way.
- **F2 — the faux-kit-root staging disappears** once no engine resolves
  `SCRIPT_DIR/../..` (`stage_door_root` and `_STAGE_MAP` shrink or go).
- **F3 — `tests/test_door_data_sync.py` retires** with the duplication;
  its "no extra files" direction survives wherever a data store remains.
- **F4 — behavior pinned before the port**: the existing
  `tests/agentive_kit/test_door_e2e.py` suite is the characterization
  net; it must pass unchanged (or with deliberate, listed diffs) after
  consolidation.
- **F5 — kit-tree callers survive**: anything still invoking
  `scripts/local/engine-*.sh` directly (materials flow until KIT-0107,
  `.kit`-internal tooling, tests) is re-pointed or retired in the same
  PR.

## Acceptance

- [ ] Each engine has exactly one source path — pinned by an
      EXECUTABLE assertion that fails while both the kit-tree and
      packaged copies exist (an absent `_SYNC_SOURCES` map proves
      nothing on its own; grep proof in the PR body as a supplement)
- [ ] `agentive new` / `agentive adopt` E2E suite green with no
      kit-tree engine copies
- [ ] The full suite is green on both macOS (bash 3.2/BSD) and CI Linux

## Notes

- Pinned pair: KIT-0107 (shim removal) shares the 0.10.0 pin.
- Scope guard: this is the follow-up KIT-0104 explicitly declared out
  of its own scope ("port, not rewrite") — the rewrite happens HERE,
  against the E2E net, never mid-port.
- **Rider (planner, 2026-08-14, from the PR #130 deep evaluator —
  dispositioned there, decide-explicitly here)**: a root-anchored
  target (`agentive new /x`) resolves the preset home to
  `/agentive-config` (edge of the PR 1 target-parent anchor decision;
  today seeding requires the directory to pre-exist, so nothing is
  created at root). During consolidation, make the root-parent case
  an explicit decision — refuse, warn, or document — rather than an
  emergent one. Source: `.kit/context/KIT-0104-REVIEW-STARTER.md`
  PR 2 section.
