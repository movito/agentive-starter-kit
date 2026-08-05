# KIT-0060: Refresh plugin skill copies + source map after the skills merge

**Status**: Canceled
**Priority**: low
**Assigned To**: unassigned
**Estimated Effort**: <1 hour
**Created**: 2026-07-21
**Target Completion**: next agentive-workflow plugin release

> **SUPERSEDED NOTE (0.9.0, planner 2026-07-28)**: any
> `.kit/skills/` reference below is historical — that home was
> removed at 0.9.0 (KIT-0059); skills live only in `.claude/skills/`.
> Re-scope against current main before promoting this task.

> **Archived (2026-08-04, backlog review)**: its subject (`.kit/skills/`) was removed at 0.9.0 (KIT-0059) per its own superseded note; a <1h task needing a full re-scope is a re-file, not a keep. Re-file against current main if plugin skill copies drift again.

## Related Tasks

**Parent**: KIT-0057 (canonical homes + the prune) / KIT-ADR-0027 P6
**Related**: KIT-0030 (plugin consolidation — created the copies and
`CONSOLIDATION.md`'s source map)

## Overview

KIT-0057 moved the three builder skills to `.claude/skills/` and edited
their text (cross-references now cite the canonical home). Per N2 the
plugin repo (`~/Github/agentive-skills`) was NOT touched in that PR —
this task carries the change into the next plugin release. Plugin
namespacing (`agentive-workflow:<name>`) is unaffected; the plugin's
`skills/` home is flat and stays flat.

## Requirements

- Re-copy the five skills from the kit's `.claude/skills/` into
  `plugins/agentive-workflow/skills/` (the copies drifted when
  KIT-0057 edited `pre-implementation` and `code-review-evaluator`).
- Update `CONSOLIDATION.md`'s source map: the four blocks listing
  `.kit/skills/<name>/SKILL.md` as upstream sources now point to
  `.claude/skills/<name>/SKILL.md`.
- Bump the plugin version (semver: patch — content refresh, no
  interface change) and follow the plugin release flow.

## Acceptance Criteria

- [ ] Plugin skill copies byte-match the kit's canonical
      `.claude/skills/` versions
- [ ] `CONSOLIDATION.md` source map cites the canonical home
- [ ] Plugin version bumped; downstream pins unaffected until they
      take the release
