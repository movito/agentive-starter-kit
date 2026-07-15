# KIT-0054: Remove the entrance shims (KIT-0053 follow-through)

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 1-2 hours
**Created**: 2026-07-15
**Target Completion**: **PINNED — next minor release (0.9.0)**. This
deadline is the ADR-0027 P3 enforcement mechanism, not a suggestion:
unenforced "one release later" deprecation is how the kit accumulated
six setup doors in the first place. Filed on the same PR that created
the shims (the ADR's non-negotiable pairing).

## Related Tasks

**Parent**: KIT-0053 (the one setup door) / KIT-ADR-0027 P3
**Blocks**: nothing — but 0.9.0 must not ship with the shims still in

## Overview

KIT-0053 turned the three historical entrances into frozen-surface
shims that exec `scripts/local/bootstrap` (`--legacy-shim`):

- `scripts/local/bootstrap-consumer.sh` → door `--adopt`
- `scripts/local/bootstrap.sh` → door `--adopt --design-materials`
- `scripts/optional/create-project.sh` → door `--new`

This task deletes them, plus the door's `--legacy-shim` fidelity
channel that exists only for them.

## Requirements

- Delete the three shim files.
- Remove `--legacy-shim` handling from `scripts/local/bootstrap`
  (parse case, the legacy exec block, and the forced-profile-note
  suppression) — after this, every door run gets chrome + offers +
  doctor tail.
- Retarget the characterization suites at the door's own surface:
  `tests/test_bootstrap_shapes.py` invokes the old entrance path —
  port its shape/profile/record coverage to door flags (the engine
  behavior stays pinned); drop the shim-surface tests in
  `tests/test_entrance_shims.py` (keep the engine e2e + call-graph
  tests). `tests/test_setup_door.py` `test_legacy_shim_channel_is_
  chrome_free` goes with the channel.
- Sweep references: grep `bootstrap-consumer.sh`, `bootstrap.sh`,
  `create-project.sh` across docs/agents — KIT-0053 PR 2 already
  converged them on the door, so only historical mentions should
  remain (leave retro/ADR history untouched).

## Acceptance Criteria

- [ ] Three shims deleted; `--legacy-shim` gone from the door
- [ ] Old entrance paths hard-fail (no silent fallbacks)
- [ ] Shape/profile/record characterization re-pinned on door flags
- [ ] Full suite green; no doc references outside historical records

## Notes

- **Known shim/door divergence that this removal erases** (BugBot
  PR #81, declined on N1): the native door rejects an explicit
  `--shape`/`--profile` that contradicts the target's existing
  kit-install record (exit 2); the legacy shim path preserves the
  historical silent-preserve behavior (exit 0), because a conflicting
  re-adopt was a *succeeding* historical invocation form and N1 pins
  it. When the shims and `--legacy-shim` go, every adopt gets the
  conflict check automatically — nothing extra to implement, but
  re-pin the characterization to the door's corrected semantics.
- **Materials-engine hardening to consider here** (CodeRabbit PR #81,
  declined on the frozen legacy surface): `engine-materials.sh` runs
  the TARGET's copy of `setup-dev.sh` (rsync `--ignore-existing`
  preserves a pre-existing one), i.e. target-controlled code executes
  with the operator's privileges. Declined for KIT-0053 because the
  flow's trust boundary is the operator's choice of directory (the
  same materials are handed to an interactive claude agent moments
  later) and the surface is characterization-frozen. When the shims
  die, consider executing the KIT's copy with `cwd=$TARGET` instead —
  and re-pin the characterization accordingly.
- Consumers hold frozen copies of the old `create-project.sh` from
  pre-KIT-0053 bootstraps; those keep working (they are full
  implementations, not shims). Fresh consumers get the shim, which
  fails loudly with guidance when the kit-side door is absent —
  removal does not change the consumer story.
