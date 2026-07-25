# KIT-0065: Purge aider-era evaluator scripts and stale references

**Status**: In Progress
**Priority**: medium
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

### Widened scope (2026-07-24, from the pre-0.9.0 cruft audit)

Whole-repo aider residue. Evidence with exact lines:
`.kit/context/reviews/PRE-090-CRUFT-AUDIT-2026-07-24.md` (A-numbers):

- **F6 (A03) — the Python `<3.13` ceiling**: `project setup` attributes
  the bound to the retired aider-chat dep in three places
  (project:632/646/657), and pyproject pins
  `requires-python = ">=3.10,<3.13"` with no surviving rationale.
  RE-DERIVE the bound: check what adversarial-workflow>=1.0.1 and the
  rest of the dev stack actually require on 3.13+. If liftable, lift
  it (pyproject + setup messages + CI matrix in the same PR); if not,
  document the REAL constraint at the pin. This is the one behavioral
  item — everything else is text.
- **F7 (A09)**: `.aider` entry in `project`'s `exclude_dirs` — drop.
- **F8 (A27)**: test-runner.md claims a `--yes` CLI flag (phantom-flag
  class) — replace with the standing `echo y | ADVERSARIAL_UNATTENDED=1`
  invocation.
- **F9 (A29)**: five agents tell readers to
  `cat .adversarial/logs/TASK-*-PLAN-EVALUATION.md` (aider-era log
  naming) — fix to the current `<input>--<evaluator>.md` scheme.
- **F10 (A30)**: onboarding.md repeats the aider-chat constraint text.
- **F11 (A47)**: `.kit/templates/AGENT-TEMPLATE.md` bakes
  `aider --yes` into every generated agent — fix the template AND
  grep generated agents for inherited copies.
- **F12 (A76)**: `tests/test_project_script.py` pins the aider-chat
  message — update alongside F6's message rewrite (fixture-honesty:
  test the NEW message).
- **Closure criterion**: `grep -ri aider` over the repo returns only
  historical records (retros, done tasks, ADRs, review records,
  CHANGELOG) and the pyproject floor comment. Paste the final grep
  in the PR body.

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
