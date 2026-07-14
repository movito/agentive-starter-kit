# KIT-0048 Handoff — feature-developer

**Task**: `.kit/tasks/5-done/KIT-0048-planning-repo-shape.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-14 (planner-f5)
**Estimated effort**: 4–6 hours

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0048/`** — branch
`feature/KIT-0048-planning-repo-shape`, fully provisioned. Run
`git pull --ff-only` first (the worktree was cut just before this spec
landed on main).

## Mission

ADR-0027 P2 — the strategic split: planning repos get coordination
machinery with zero Python toolchain; target repos get nothing. After
this merges, adopting the kit for a non-Python product is "create a
sibling planning repo in minutes". Transformation task 2 of 6.

## Verified runtime facts (planner, 2026-07-14)

- `scripts/core/project` is stdlib-only on system `python3 ≥ 3.11`
  (`tomllib` stdlib since 3.11; `gql`/`dotenv` imports are confined to
  the optional Linear-sync path at lines ~1585-1588, inside the
  lazy/generated section — verify their guard still degrades gracefully
  before relying on it, and paste the check in the PR).
- Doctor's shape seam: `# TODO(P2): per-shape inclusion` in the
  KIT-0046 driver — your F3 target. Doctor.d checks are individual
  files; the accepted design is a `# shapes:` header per check, driver
  reads the shape record once.
- Shape record mechanics: `kit_markers.py` (`merge`/`extract_region`/
  `replace_region`) is the ONLY writer/reader — region name
  `kit-install`. Marker lines are whitespace-tolerant but keep the
  canonical form; the fenced-code fail-fast non-goal is documented in
  DISTRIBUTION-ARCHITECTURE.md.
- `bootstrap-consumer.sh` already has the KIT_AGENTS/AGENT_EXCLUDES
  single-sourcing and the `.kit/` scaffold path — `--shape planning` is
  a branch inside it, not a new script. The marker-membership test
  (`test_bootstrap_consumer.py`) must stay green.

## Implementation guidance

- **Characterization FIRST (N1)**: before touching the script, capture
  flagless bootstrap output against a scratch consumer; assert
  `--shape single` and flagless stay byte-identical throughout. This is
  your regression net for every subsequent edit.
- **F1 file-sets**: two enumerated lists (ship / never-ship) as
  variables near KIT_AGENTS, same single-sourcing style. The never-ship
  list for planning is part of the contract — test both directions
  (present in single, absent in planning).
- **F2 region**: write `shape: planning` + target pointer
  (`target_path`, `target_github`) via kit_markers; also seed the
  human-facing `## Target Repository` section (existing KIT-ADR-0024
  convention — agents grep for it; do NOT change their detection).
  Fresh-bootstrap placeholder vs `--target-*` flags: take the flags
  when given, placeholder otherwise (marker-merge preserves consumer
  edits on re-bootstrap, as with all KIT-LOCAL regions).
- **F3 doctor**: per the spec — `# shapes:` declarations, absent
  record = single, malformed = full set + `DOCTOR:shape-record:FAIL`.
  Add the header to all eight existing checks (most are
  `single planning`; venv/skew/Black are `single`-only).
- **F4 pre-commit**: a minimal planning variant (whitespace, eof,
  validate-task-status). `validate_task_status.py` must be in the
  planning ship-list for the hook to work — check its imports are
  stdlib.
- **F5**: annotate + retire KIT-0027 (backlog → superseded; follow the
  ASK-0048 disposition-note precedent — keep the file, mark it).

## Test approach

- **Ordering rule (now ALL tasks, KIT-0046 widening)**: local tests
  green → run the evaluator trio → THEN open the PR. `git status`
  after every evaluator run.
- Scratch e2e per the spec's acceptance criteria (mktemp; KIT-0033
  pattern; conftest GIT_* isolation covers subprocess git).
- `pytest` directly; `./scripts/core/ci-check.sh` before pushing.
- Doctor runs from both shapes pasted in the PR description.

## Evaluation summary

`arch-review-fast`: REVISION_SUGGESTED — two findings accepted
(check-level shape declarations; malformed-shape fail-loud), one
deferred to P3 with reasoning (declarative file-sets). Disposition in
the task file; log:
`.adversarial/logs/KIT-0048-planning-repo-shape--arch-review-fast.md`.
No outstanding blockers.

## Out of scope

- P1 profiles, P3 door, P7 presets (the `--shape` flag is the interim
  entrance; it becomes a shim argument at P3)
- Migrating existing planning repos (post-P3 checkpoint)
- Any write to any target repo (N3 is absolute)
- Doctor driver redesign beyond the seam (KIT-0046 shipped it)

## PR sizing

Single PR (< 500 lines: bootstrap branch + file-set lists + region
write + doctor headers + pre-commit variant + tests): branch
`feature/KIT-0048-planning-repo-shape` (already created). If the
characterization tests balloon it, they may land as a small PR 1 —
planner pre-approves that split.
