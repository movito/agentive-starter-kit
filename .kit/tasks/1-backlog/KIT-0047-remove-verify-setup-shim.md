# KIT-0047: Remove the verify-setup.sh shim

**Status**: Backlog
**Priority**: low
**Assigned To**: unassigned
**Estimated Effort**: <1 hour
**Created**: 2026-07-14
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0046 (`project doctor` — filed this removal per the
ADR-0027 shims-with-filed-removal rule)

## Overview

`scripts/core/verify-setup.sh` became a deprecation shim around
`./scripts/core/project doctor` in KIT-0046. Once downstream consumers
have synced a core-scripts version that includes doctor (and their docs
no longer reference verify-setup.sh), delete the shim.

## Acceptance Criteria

- [ ] No references to `verify-setup.sh` remain in this repo's docs,
      agents, commands, or workflows (grep before deleting)
- [ ] Downstream consumers are on a core version ≥ the one that shipped
      doctor (check before removal; ADV/DSP/AEL sync status)
- [ ] `scripts/core/verify-setup.sh` deleted; manifest entry removed and
      counts in `tests/test_core_manifest.py` updated in the same commit

## Notes

- The shim forwards `$@` and exits with the doctor exit-code contract
  (0 ok / 1 fail / 2 warn-only / 3 driver error) — callers scripting
  against the old "0 or 1" contract already needed review at shim time.
