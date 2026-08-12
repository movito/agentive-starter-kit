# KIT-0103: Post-phase-4 residue — stale sync references + stale-project warning

**Status**: Backlog
**Priority**: low (rides the next plugin release train; nothing
urgent — the affected population is ~zero)
**Type**: Cleanup
**Estimated Effort**: 2-3 h
**Created**: 2026-08-12
**Source**: KIT-0102 PR #127 follow-ups (both operator-visible on the
PR threads / review starter)
**Evaluation**: skipped (planner) — enumerated cleanup, decisions made
below

## R1 — release-train cleanup of stale sync references

Six rostered `.claude/` files still carry references to the retired
sync machinery (the KIT-0102 session enumerated them on the PR —
derive the list from there and re-grep). Fix in canon per the
grep-first sweep rule (the class grep's hit list IS the work list),
ship with the next plugin release; drift guard red-by-design between.

## R2 — stale pre-packaged project: detect-and-warn (DECIDED)

**Planner ruling (2026-08-12): detect-and-warn, NOT force-refresh.**
A pre-KIT-0102 consumer that re-bootstraps sees `❌ Sync engine
unavailable` because the door's never-overwrite invariant preserves
the old `project` script that imports the deleted engine. Force-refresh
would mutate preserved consumer files — breaking the invariant that
exists precisely to protect operator-owned state; the population is
effectively zero (one known instance: the operator's own `_old`
archive). Instead: the door detects the stale import and prints a
clear retirement notice — "this project predates the packaged era; its
copied scripts reference retired machinery — re-create via the door or
install agentive-kit and remove scripts/core" — instead of the raw
error. Portable shell; contract-string pin if the acceptance test
covers the tail.

## Acceptance Criteria

- [ ] R1: class grep opens the work, end grep proves it; ships in the
      next plugin release; drift guard green after
- [ ] R2: stale project produces the retirement notice, not the raw
      error (falsified once against the `_old` archive shape)
