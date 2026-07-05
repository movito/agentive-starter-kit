# KIT-0037: Codify a wrapper exit-code convention (reserved engine codes)

**Status**: In Progress
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 1-2 hours
**Created**: 2026-07-04
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent Task**: KIT-0036 (Pull-based consumer sync) — surfaced in its retro
**Related**: KIT-0039 (staging-scope self-review item, same retro)

## Overview

`scripts/core/sync_from_manifest.py` defines a **frozen exit-code contract**
(`0` clean/applied · `1` drift/warnings · `2` usage · `3` manifest · `4` I/O).
The `project sync` wrapper (KIT-0036 D5) initially returned `1` for
wrapper-level *hard* failures — branch-checkout failure and a missing/broken
engine import — which collides with the engine's reserved meaning of `1`
("updates available"). Automation such as the `upgrader` agent's Phase 8
`project sync --dry-run` would misread a hard failure as drift.

Three separate bot findings during KIT-0036 traced to this single principle.
Codify it once so future wrappers around a contract-bearing engine don't
re-litigate it.

## Goal

1. **Write the convention down** where implementers will see it — a short rule
   in `.kit/skills/self-review/SKILL.md` (or the self-review checklist the
   feature-developer runs at Phase 4): *A wrapper around an engine with a
   frozen exit-code contract must not reuse the engine's reserved success/drift
   codes (`0`/`1`) for wrapper-level failures. Environment/precondition
   failures (can't fetch, can't branch, engine missing) → exit `2`.*
2. **Audit the existing wrapper** (`scripts/core/project` `cmd_sync` and
   helpers) to confirm it already follows this after the KIT-0036 fixes
   (it should — branch-fail and import-fail both return `2`), and add a
   one-line comment near the exit points pointing at the convention.

## Acceptance Criteria

- [ ] Convention documented in the self-review skill/checklist
- [ ] `cmd_sync` exit points annotated with a pointer to the convention
- [ ] No wrapper-level failure path returns `0` or `1`

## References

- Retro: `.kit/context/retros/KIT-0036-retro.md` (What Should Change #2)
- Engine contract: `scripts/core/sync_from_manifest.py` (module docstring)
- Wrapper: `scripts/core/project` (`cmd_sync`, `_create_branch`)
