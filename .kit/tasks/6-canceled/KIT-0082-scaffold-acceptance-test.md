# KIT-0082: Scaffold acceptance test — the door's output must demonstrably work

> **Absorbed into KIT-0093 (2026-08-08, operator-approved)**: this task's requirements are carried explicitly by the ADR-0028 phase 2 spec (`KIT-0093-door-package-install-mode.md`, F5 scaffold acceptance test: red-first against today's door, then green by the switch; removal rule recorded in workflow docs). This file is retained verbatim as the source record; implementation and acceptance happen in KIT-0093.

**Status**: Canceled
**Priority**: high
**Created**: 2026-08-04

## Overview

The 0.9.0 cleanup achieved its goal (remove python-centric cruft, make
agent/script updates maintainable) at the cost of shipping scaffolds that
don't work out of the box. The operator's verdict after the
ev-fast-charging-loads intake (2026-08-04): "We managed to clean up the
repo, but at the cost of not shipping something that actually works."

Root cause, same lesson as KIT-0075's banked insight: **removal decisions
were scoped by directory, not by function.** Load-bearing files (`launch`,
the task template, CROSS-REPO-PATTERN.md, README) lived in swept
directories, and nothing failed when they left — because no check asserts
that a fresh scaffold is USABLE, only that the install steps ran.

This task adds that check, so a function-scoped regression is loud at PR
time instead of being discovered by the operator in a fresh project.

## Requirements

- **F1 — acceptance script**: a script (e.g.
  `scripts/core/scaffold-acceptance.sh` or pytest module) that runs
  `bootstrap --new` into a temp dir for BOTH shapes (single+python,
  planning+none) and asserts, per shape:
  - **Reference closure**: every `docs/…` and `.kit/…` path mentioned in
    the seeded `.claude/agents/*.md` and CLAUDE.md exists in the scaffold
    (the grep-and-test loop used in the 2026-08-04 audit; automate it)
  - **First moves work**: `.kit/launchers/launch` exists and is
    executable; `scripts/core/project doctor` runs with no stray stderr
    (dirname/git noise = fail); the planner Phase 1 triage paths
    (`.kit/tasks/*/`, `.kit/context/agent-handoffs.json`) exist
  - **Self-description**: README.md exists and names the repo's purpose
    (guards the "repo looks empty" failure, KIT-0081 F8)
  - **Evaluator path**: `project install-evaluators` succeeds or the
    scaffold carries what it needs (guards KIT-0079)
  - **Seeded-.env invariants** (added post-KIT-0084, PR #105): `.env`
    present, mode 0600, gitignored, `PROJECT_NAME` filled, `TASK_PREFIX`
    never `TASK`, no secret value in captured output — assertions already
    modeled in `tests/test_setup_door.py::TestEnvSeedingE2E`; reuse them
- **F2 — CI wiring**: runs on PRs touching `scripts/local/engine-*`,
  `scripts/local/bootstrap`, the export manifest, or `.claude/agents/`;
  runnable locally in < 1 min.
- **F3 — definition of done for removals**: add one line to the workflow
  docs (WORKFLOW-FREEZE-POLICY.md or COMMIT-PROTOCOL.md): a PR that
  deletes or de-ships a file must enumerate the file's FUNCTIONS and show
  the acceptance test still passes — directory-shaped deletion rationales
  are not sufficient.

## Acceptance Criteria

- [ ] Acceptance script exists and fails on today's 0.9.0 scaffold
      (proving it catches the current known gaps), passes once
      KIT-0075/KIT-0079/KIT-0081 fixes land
- [ ] Wired into CI per F2
- [ ] Removal rule recorded per F3

## Related

- KIT-0075 (launcher consumer story), KIT-0079 (evaluator pin),
  KIT-0080 (git 2.30.1 — S3 preset resolution), KIT-0081 (intake gap
  audit; its findings are this test's initial fixture list)
- Suggested sequencing: fix KIT-0080 first (environment), then land this
  test RED against the known gaps, then KIT-0081 F1–F8 + KIT-0075 F4 +
  KIT-0079 turn it green — a "0.9.1 ships-working-scaffolds" milestone.
