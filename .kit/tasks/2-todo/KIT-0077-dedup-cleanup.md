# KIT-0077: Dedup cleanup — context archive, dispatch retirement, doc archival

**Status**: Todo
**Priority**: medium (sequenced AFTER 0.9.0 merges)
**Assigned To**: unassigned
**Estimated Effort**: 3-4 hours
**Created**: 2026-07-28
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: dedup analysis
(`.kit/context/reviews/DEDUP-ANALYSIS-2026-07-28.md`) — all
dispositions operator-approved 2026-07-28
**Related**: KIT-0076 (must merge first), the future
planning/product split ADR (report §8 — this task is its
prerequisite hygiene)

## Requirements

- **F1 — context archive (the big one)**: `git mv` the 74 done-task
  HANDOFF/REVIEW-STARTER/TASK-STARTER/SESSION files (7,516 lines;
  enumerated by task-ID-in-5-done/6-canceled/7-blocked — recompute
  the list at implementation, it grows) from flat `.kit/context/`
  into `.kit/context/archive/`. Pure moves. Update any LIVE citer
  (agent-handoffs.json details_link fields for done tasks may
  point at old paths — check; historical citers stay).
- **F2 — dispatch-kit retirement (operator: no longer in use)**:
  archive `.dispatch/config.yml`; remove the `--with-dispatch`
  gate + steps from `scripts/optional/setup-dev.sh` (KIT-0067 D4
  built the gate; retirement supersedes); sweep live doc/agent
  mentions of dispatch as a current feature (patterns.yml's
  origin headers are historical — keep). Variant-sweep greps.
- **F3 — doc archival**: `.kit/docs/UPGRADE-0.4.0.md` and
  `.serena/claude-code/USE-CASES.md` (912L; operator: not in use)
  → `docs/archive/`; repoint the test-runner/powertest-runner
  agent citations and engine copy-list entries.
- **F4 — template-pair check**: `review-starter-template.md` vs
  `review-template.md` (report §4) — determine which the
  review-handoff skill actually uses; merge or archive the loser.
- **F5 — record confirmations**: builder-only commands
  (new-project/setup-preset/wrap-up absent from manifest) =
  INTENDED — add a one-line comment in the manifest or the
  commands' frontmatter noting builder-only status;
  OPERATIONAL-RULES.md = kept (no action).

## Acceptance Criteria

- [ ] .kit/context/ flat listing contains only live coordination
      files + workflows/ + retros/ + reviews/ + archive/
- [ ] No live surface cites dispatch as current, moved docs at old
      paths, or the losing template (variant greps in PR)
- [ ] Manifest/count tests updated same-commit where membership
      changes
- [ ] Planner tree verification before merge (mostly-moves diff)

## Notes

- Evaluation skipped (planner): executes an adversarially-produced,
  operator-approved analysis. Fast-only trio; tree gate.
