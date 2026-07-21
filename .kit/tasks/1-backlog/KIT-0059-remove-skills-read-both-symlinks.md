# KIT-0059: Remove the .kit/skills read-both symlinks (KIT-0057 follow-through)

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: <1 hour
**Created**: 2026-07-21
**Target Completion**: **PINNED — next minor release (0.9.0)**. Same
enforcement mechanism as KIT-0047 and KIT-0054: the shims-with-filed-
removal rule — an unenforced "one release later" deprecation is how the
kit accumulated two skills homes in the first place. Filed on the same
PR that created the symlinks (the ADR's non-negotiable pairing).

## Related Tasks

**Parent**: KIT-0057 (canonical homes + the prune) / KIT-ADR-0027 P6
**Siblings in the 0.9.0 removal set**: KIT-0047 (verify-setup shim),
KIT-0054 (entrance shims)
**Blocks**: nothing — but 0.9.0 must not ship with the symlinks still in

## Overview

KIT-0057 merged the two skills homes into `.claude/skills/` and left
`.kit/skills/<name>` as relative symlinks for one release (the
read-both deprecation cycle, N1). This task ends the cycle.

## Requirements

- Delete the three symlinks: `.kit/skills/code-review-evaluator`,
  `.kit/skills/review-handoff`, `.kit/skills/self-review` — and the
  now-empty `.kit/skills/` directory.
- Retarget the manifest: the `kit_builder` tier's `.kit/skills/` entry
  in `scripts/.core-manifest.json` becomes `.claude/skills/` (or is
  dropped if the tier review says `.claude/` distribution suffices) —
  keep `tests/test_core_manifest.py` counts in sync in the same commit.
- Delete `TestReadBothDeprecationCycle` from
  `tests/test_skills_homes.py` (its docstring names this task); keep
  `TestCanonicalHome`, dropping the deprecated-home guard clause.
- Grep first (the N3 rule): `grep -rn '.kit/skills'` must show only
  historical records (ADRs, done tasks, retros) before deleting.
- Update `docs/MANIFEST-UPGRADE-GUIDE.md`'s example manifest alongside
  the real one.

## Acceptance Criteria

- [ ] No `.kit/skills/` in the tree; full suite green
- [ ] Manifest + manifest tests updated together
- [ ] Reference grep output in the PR shows only historical records
