# KIT-0065: Purge aider-era evaluator scripts and stale references

**Status**: Backlog
**Priority**: low
**Assigned To**: unassigned
**Estimated Effort**: 1 hour
**Created**: 2026-07-24
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Related**: KIT-0025 (PR-based evaluator runner — proposed replacing
`review_implementation.sh`; this task removes rather than replaces),
KIT-0044 (root-caused the 0.9.7 aider-era working-tree mutation)

## Overview

Aider is no longer used anywhere (operator confirmation 2026-07-24;
upstream adversarial-workflow removed it in 1.0.x, and the
`>=1.0.1` floor now enforces that in pyproject). Four scripts in
`.adversarial/scripts/` still invoke the `aider` command directly and
would fail if run: `review_implementation.sh`, `evaluate_plan.sh`,
`validate_tests.sh`, `proofread_content.sh`. The current evaluation
path is the `adversarial` CLI + `prepare-review-input.sh`; these are
dead 0.9.x scaffolding. Two live surfaces still reference them.

## Requirements

- **F1**: verify first whether `adversarial init` (1.0.x) provisions
  these scripts — if it does, deletion locally will resurrect on
  downstream inits; coordinate with what 1.0.x actually ships before
  deleting (self-review item 10: check the installed tool, not
  memory).
- **F2**: delete the four aider-invoking scripts from
  `.adversarial/scripts/` (subject to F1's finding).
- **F3**: fix live references: `.claude/agents/create-project.md` and
  `.adversarial/docs/EVALUATION-WORKFLOW.md` point at the current
  CLI + `prepare-review-input.sh` flow instead.
- **F4**: `tests/test_project_script.py:356` drops the
  `"aider-chat"` alternative from its assertion.
- **F5**: leave historical records untouched (retros, done tasks,
  ADR-0004, memory files) — they describe what happened.
- Out of scope: `.claude/settings.local.json` `Bash(aider:*)` allow
  entry (user-owned; operator removes at leisure).

## Acceptance Criteria

- [ ] F1 finding documented in the PR (what 1.0.x `init` ships)
- [ ] No file outside historical records invokes or instructs
      invoking `aider`
- [ ] Tests green; evaluation flow demonstrably unaffected
      (one trio run in the PR)

## Notes

- Evaluation skipped (planner): deletion/cleanup with decisions
  in-spec; F1 is the only open question and it's a verification step.
- Origin: operator FYI during dependabot sweep #2 (2026-07-24) +
  planner grep audit.
