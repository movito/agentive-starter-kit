# KIT-0064: Door warns when exporting from a dirty kit tree

**Status**: Backlog
**Priority**: low
**Assigned To**: unassigned
**Estimated Effort**: <1 hour
**Created**: 2026-07-24
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0058 retro (What Should Change #3, Incident Closure #1)
**Related**: KIT-0053 (the one door), `scripts/local/engine-export.sh`

## Overview

`bootstrap --new` exports via `git archive`, which ships HEAD — not the
working tree. On KIT-0058, the one-button demo ran before the first
commit, so the exported target's `doctor.d/` silently lacked the
uncommitted `90-config-home.sh` (doctor tail showed 9 checks instead
of 10). Diagnosed in a minute, but nothing in the door's output says
uncommitted kit changes don't ship — the demo-confusion class is real
for anyone iterating on the kit itself.

## Requirements

- **F1**: in the door's export path, when the kit tree has uncommitted
  changes (`git status --porcelain` non-empty, scoped to tracked
  files), print a one-line notice: "kit tree has uncommitted changes —
  the export ships the last commit (HEAD)". Notice only, never a
  block; exit code unchanged.
- **F2**: test in `tests/test_setup_door.py` (dirty tree → notice
  present; clean tree → absent).

## Acceptance Criteria

- [ ] Notice printed on dirty-tree export, absent on clean
- [ ] Exit codes and export behavior otherwise unchanged
- [ ] Tests for both directions

## Notes

- Evaluation skipped (planner): single-notice change, decisions
  in-spec. Incident evidence:
  `.kit/context/retros/KIT-0058-retro.md` (Surprising #1).
- Not a doctor.d candidate — the condition lives in the SOURCE tree at
  export time, not the installed environment doctor inspects (retro's
  own triage).
