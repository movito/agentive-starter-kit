# KIT-0061: Fix the 2.0.0 consumer-manifest seed + guard EVERY baked manifest

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 1-2 hours
**Created**: 2026-07-21
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0057 retro (Process Actions change 4 — planner
disposition) + PR #90 CodeRabbit thread (Data Integrity)
**Related**: KIT-0057 F3 (the baked-manifest guard this generalizes —
it covers the PLANNING-shape heredoc; the single-shape/consumer seed
escaped it)

## Overview

The consumer-manifest heredoc in the engine still hard-codes
`core_version: 2.0.0` (real value: 3.x) and can mask newer files. The
KIT-0057 F3 guard asserts heredoc==VERSION for the planning-shape seed
only — the same class lives in every other baked manifest. Fix the
stale seed and make the guard enumerate ALL baked manifests so the
class is test-caught, never review-caught again.

## Requirements

- **F1**: fix the stale `2.0.0` seed (and the adjacent description
  TODO the retro notes) to track `scripts/core/VERSION`.
- **F2**: extend `tests/test_core_manifest.py`'s KIT-0057 guard to a
  table over EVERY baked manifest/heredoc in the engines (enumerated
  list, not a glob — find them all first; state the inventory in the
  PR). Each entry asserts its baked `core_version` == VERSION.
- **F3**: prove the extended guard fires (scratch desync per entry
  class, KIT-0057 precedent).

## Acceptance Criteria

- [ ] No baked manifest anywhere carries a stale core_version (guard
      green across the enumerated table)
- [ ] Guard proven to fire on desync
- [ ] Inventory of baked manifests stated in the PR

## Notes

- Evaluation skipped (planner): single-concern fix + guard extension
  of an already-evaluated mechanism (KIT-0057 F3) — the skip category.
- Not 0.9.0-pinned; schedule freely (small).
