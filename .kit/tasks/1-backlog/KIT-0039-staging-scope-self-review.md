# KIT-0039: Self-review item — commit staging scoped to changed paths

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 1 hour
**Created**: 2026-07-04
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent Task**: KIT-0036 (Pull-based consumer sync) — surfaced in its retro
**Related**: KIT-0037 (wrapper exit-code convention, same retro)

## Overview

The "stage whole roots / `git add -A`" pattern produced review findings
**twice** in KIT-0036: first in `sync-core-scripts.yml` (`git add -A`, PR 1),
then in `project sync`'s `_stage_and_commit` (`git add scripts .claude/commands
.kit .adversarial`, PR 2). In both cases an automated commit could sweep
unrelated uncommitted work in those trees into the sync commit. The fix in each
case was to stage only the exact changed paths (from the sync report /
manifest).

Because it recurred within one task, it's worth a durable self-review guard.

## Goal

Add a self-review checklist item (in `.kit/skills/self-review/SKILL.md`) and,
optionally, a `pattern_lint` rule:

> **Scoped staging**: any helper that programmatically `git add`s + commits
> must stage the *exact* changed paths it produced (from a report/manifest),
> never whole roots or `git add -A` / `git add .` — unless the working tree is
> provably clean (e.g. a fresh CI checkout, and even then prefer scoping).
> Deleted files are staged as deletions via `git add -- <path>`.

Consider a lightweight `pattern_lint` heuristic that flags `git add -A` /
`git add .` / `git add <dir>` inside Python/shell helpers that also `git
commit`, so it's caught pre-commit rather than by a bot.

## Acceptance Criteria

- [ ] Self-review checklist gains the scoped-staging item
- [ ] (Optional) `pattern_lint` heuristic + test, or a documented decision not to
- [ ] No regression: the KIT-0036 fixes (`_stage_and_commit`, workflow scoped
      adds) remain the reference implementation

## References

- Retro: `.kit/context/retros/KIT-0036-retro.md` (What Should Change #4)
- Reference impl: `scripts/core/project` (`_stage_and_commit`),
  `.github/workflows/sync-core-scripts.yml` (scoped `git add` loop)
