# KIT-0049: Shape-scoped `project sync`

**Status**: Backlog
**Priority**: high (raised by planner 2026-07-14: this completes P2's
promise — planning repos are live but update-locked until it lands.
Recommended sequence: KIT-0049 next, small and unblocking, then P1.)
**Assigned To**: unassigned
**Estimated Effort**: 2-3 hours
**Created**: 2026-07-14
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0048 (planning-repo shape) — filed from a BugBot finding
on PR #78
**Related**: KIT-ADR-0026 (the sync engine), ADR-0027 P3 (the one door —
may absorb or reshape this)

## Overview

`sync_from_manifest.py` selects entries from the UPSTREAM manifest's
tiers, so a full `project sync` into a planning-shaped repo would
install the single-shape toolchain files (`ci-check.sh`,
`pattern_lint.py`, …) the shape must never ship, and would replace the
reduced planning manifest with upstream's full one.

KIT-0048 shipped the stopgap: `cmd_sync` reads the shape record and
**refuses** (exit 2, wrapper convention) with a pointer here. This task
makes sync shape-aware.

## Requirements

- The engine (or the wrapper) must intersect upstream entries with the
  shape's ship-list — the planning list currently lives as
  `PLANNING_CORE`/`PLANNING_LOCAL` in `bootstrap-consumer.sh`; decide
  the single source (likely: move the list somewhere both can read, or
  have sync respect the CONSUMER manifest's file list for scripts_core).
- The replaced-manifest problem: a complete sync must not overwrite the
  planning manifest's reduced file list with upstream's full list.
- Remove the KIT-0048 refusal guard once subsets work; keep the
  malformed-shape refusal.
- Coordinate with P3 (one door): if P3 lands first, this may become a
  door behavior instead of a sync flag.

## Acceptance Criteria

- [ ] `project sync` in a planning-shaped repo updates ONLY the
      planning ship-list files and preserves the reduced manifest
- [ ] Single-shape sync behavior unchanged
- [ ] The KIT-0048 guard replaced by working subset logic
