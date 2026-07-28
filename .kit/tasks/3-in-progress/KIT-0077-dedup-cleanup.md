# KIT-0077: Dedup cleanup — context archive, dispatch retirement, doc archival

**Status**: In Progress
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

## Implementation findings (feature-developer, 2026-07-28)

- **F4 verdict: keep both templates — no merge, no archive.** The §4
  "conceptual duplicate" is refuted by the citers; they do different
  jobs and each has exactly one live consumer:
  - `review-starter-template.md` ← `.claude/skills/review-handoff/SKILL.md`
    (implementer → reviewer; becomes `<TASK-ID>-REVIEW-STARTER.md`)
  - `review-template.md` ← `.claude/agents/code-reviewer.md`
    (the reviewer's own output: verdict + criteria table)
  Both roles are now named in `.kit/context/README.md` so a future
  dedup pass does not re-raise the question. Nothing to repoint.
- **F1 was larger than specced**: 100 files, not 74 — the 0.9.0 tasks
  completed after the analysis, and `8-archive` is terminal too (the
  spec named only 5/6/7).
- **Two consumer-leak regressions were introduced and fixed**: moving
  files into `context/archive/` put them below both engines' depth-1
  sweeps. `engine-export.sh` needed `rm -rf .kit/context/archive/`;
  `engine-materials.sh` needed `--exclude='context/archive/'`. The
  materials leak was caught by the existing
  `test_engine_materials.py::test_no_task_id_files_in_kit_dirs`; the
  export path had no equivalent guard, so one was added
  (`test_setup_door.py::test_new_export_carries_no_planning_corpus`).
- **`agent-handoffs.json` needed no edit** — its only path fields point
  at the live KIT-0077 handoff (verified, not assumed).
- **Deliberately out of scope**: `movito/dispatch-kit` as a *downstream
  sync target* (sync-core-scripts.yml, DISTRIBUTION-ARCHITECTURE.md,
  KIT-0026/0031/0045/0072) is a different thing from the retired local
  integration; the guarded emit blocks in shipped scripts still serve
  it. See the PR body.
