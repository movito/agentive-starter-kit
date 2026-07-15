# KIT-0053 Handoff — feature-developer

**Task**: `.kit/tasks/3-in-progress/KIT-0053-one-setup-door.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-15 (planner-f5)
**Estimated effort**: 5–7 hours (largest transformation task; 2-PR
split pre-approved on the door/shims boundary)

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0053/`** — branch
`feature/KIT-0053-one-setup-door`, fully provisioned. Run
`git pull --ff-only` first. Shell cwd resets to the primary between
Bash calls — absolute paths / `git -C` throughout (standing pattern,
WORKTREE-WORKFLOW.md).

## Mission

ADR-0027 P3, transformation 4 of 6: one entrance
(`--new`/`--adopt` × shape × profile), the legality matrix with a
single owner, the three old doors as exec shims with their removal
task filed in the same PR. After this: the post-P3 downstream
checkpoint opens, and P5+P7 fill the resolution seam you leave.

## Verified entrance inventory (planner, 2026-07-15)

- `scripts/optional/create-project.sh` — clean new-project export
  (git archive, strip, customize)
- `scripts/local/bootstrap.sh` — adopt-with-design-materials
- `scripts/local/bootstrap-consumer.sh` — kit-file sync/adopt;
  carries the shape/profile implementation and is the kit-install
  record's ONLY writer (keep it that way — the door resolves, the
  engine writes)
- Plus: onboarding launcher (`.kit/launchers/onboarding`),
  `setup-dev.sh` (venv; offer under profile=python), docs tables.

## Context you must not lose

- **Shim direction is load-bearing (F3)**: call graph is strictly
  `old-name shim → door → engine`. The engines are the CURRENT
  implementations — move them behind internal entry points (rename in
  place, or an internal flag the door passes); the old filenames
  become flag-mapping exec shims. Never let the door exec an old
  entrance name — that's a loop.
- **The matrix stays in the door as a constant** (evaluation decline —
  third appearance of the externalize-to-YAML suggestion; do not
  re-litigate). Resolve/validate/orchestrate as separate testable
  functions (accepted finding).
- **The preset seam (F5) is a stub with a documented shape**: CLI →
  preset-stub (returns nothing) → defaults → prompt. P7 replaces the
  stub. Don't read any file there yet.
- **Removal task files in the same PR as the shims** (PR 2 if you
  split) — the ADR's enforced-deadline rule exists because
  doc-only deprecation is how six doors happened. Pin it to the next
  minor release.
- **Doctor ends every door run** (F1): report its verdict prominently;
  don't encode it in the door's exit (F6 contract: 0 install-ok /
  1 install-failed / 2 usage-or-illegal).
- **N4 matters for your own kind**: every prompt needs a flag
  equivalent; a non-TTY run with a missing answer fails with usage,
  never hangs. Test both.

## Implementation guidance

- Characterize the THREE old entrances first (current flag surfaces on
  scratch targets) — that's the shim-mapping net (N1). KIT-0048/0050
  precedent; goldens as a commit boundary.
- Door language: bash consistent with the entrance family it fronts,
  or python if resolve/validate testing pulls that way — your call,
  stated in the PR. Remember `intersection_names_drops` applies to the
  matrix validator's messaging (name the legal pairs on rejection).
- Sequencing suggestion: engines-behind-internal-names → door
  (resolve/validate/orchestrate) → doctor integration → PR 1;
  shims + flag-mapping characterization + docs convergence + removal
  task → PR 2.
- Self-review items 8 (door exit contract), 10 (any hint the door
  prints about other tools gets verified against installed versions),
  12 (you'll be moving implementation blocks — check the borders).

## Test approach

- **Ordering rule (all tasks)**: local tests green → evaluator trio →
  PR open; `git status` after every evaluator run. Note the
  large-input confirm: `echo y |` remains the documented pattern; if
  an evaluation auto-cancels (exit 0!), check the LOG FILE before
  believing anything ran — and record actual behavior (KIT-0052 notes
  track the open contradiction; your data point is welcome).
- Matrix cell coverage (all 6), shim characterization, non-TTY paths,
  door exit codes, scratch e2e both modes × both shapes.
- `pytest` directly; `./scripts/core/ci-check.sh` before pushing.

## Evaluation summary

`arch-review-fast`: REVISION_SUGGESTED — internal decomposition
accepted (resolve/validate/orchestrate); matrix externalization
declined with reasoning (third appearance; six cells, one owner,
constant-in-door). Disposition in the task file; log:
`.adversarial/logs/KIT-0053-one-setup-door--arch-review-fast.md`.
No outstanding blockers.

## Out of scope

- Presets (P7 fills your stub), bots-declaration/degraded modes (P5)
- KIT-0051/0052; downstream migration (opens AFTER this)
- Changing engine behavior (door orchestrates; engines unchanged
  beyond entry-point renaming)

## PR sizing

PR 1 (door + matrix + engine entry points + doctor integration,
< 500 lines) and PR 2 (shims + characterization + docs + removal-task
filing, < 300 lines) — or one PR if it stays under ~600. Branch
`feature/KIT-0053-one-setup-door` (already created).
