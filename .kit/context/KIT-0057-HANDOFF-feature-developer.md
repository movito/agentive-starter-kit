# KIT-0057 Handoff — feature-developer

**Task**: `.kit/tasks/3-in-progress/KIT-0057-canonical-homes-and-prune.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-19 (planner-f5)
**Estimated effort**: 4–6 hours

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0057/`** — branch
`feature/KIT-0057-canonical-homes-prune`, fully provisioned. Run
`git pull --ff-only` first. Absolute paths / `git -C` throughout.

## Mission

ADR-0027 P6 — the LAST task of the transformation arc. One canonical
home per artifact type, the identity blur pruned, and the two
KIT-0056 seam-guards landed. When this merges: the arc is complete,
0.9.0 becomes cuttable, and the downstream pass begins.

## Context you must not lose

- **Inventory BEFORE the move (F1 gate)**: the skills merge is
  inventory-gated by the ADR — commit the reference inventory (repo
  greps + the plugin repo `~/Github/agentive-skills` refs) as its own
  artifact before any file moves. If the plugin repo needs changes,
  FILE the follow-up, don't reach into it (N2).
- **Read-both, never hard-move** (N1): one release of dual-path
  reading for skills, tested FROM BOTH PATHS, with the removal task
  filed pinned to 0.9.0 — joining KIT-0047 and KIT-0054 in that
  release's removal set.
- **Module-skip trap on file moves** (TESTING-WORKFLOW, KIT-0053
  lesson): after ANY move, `grep allow_module_level tests/` and
  confirm no guard silently switched a suite off. This task is
  move-heavy — the trap's natural habitat.
- **pyproject identity (F2)**: characterize the `--new` export's
  customize step BEFORE renaming the kit's own package — the export
  must keep producing placeholder-free targets. The name becomes
  `agentive-starter-kit`.
- **The guards are one-liners with teeth**: F3 asserts the
  engine-consumer heredoc's `core_version` == `scripts/core/VERSION`
  (prove it fires with a scratch desync). F4 is the conformance
  harness — one fixture table through all three bots-declaration
  readers, INCLUDING duplicate-key first-wins (now blessed contract:
  patterns.yml `record_duplicate_keys_first_wins` — pin it, don't
  re-litigate it).
- **Prune discipline** (N3): nothing is deleted that a grep still
  references; KIT-0047/0054-pinned artifacts explicitly survive.
  `.kit/adversarial/` is user-owned — never stage or delete it
  (Project Context rule).

## Implementation guidance

- Suggested order: inventory artifact → F3+F4 guards (independent,
  land early) → skills merge + read-both + removal-task filing →
  pyproject rename with export characterization → optional/stray
  audit → docs convergence (F5).
- Self-review items that bite: 7 (any moved test touching
  scripts/local must keep its consumer-rsync exclusion), 12
  (move-heavy = block-border checks everywhere), 13 (read-both ×
  two-homes cells: which reader hits which path in which mode?).
- Evaluator invocation: `echo y | ADVERSARIAL_UNATTENDED=1
  adversarial …`; log-file-with-verdict is the proof, never exit 0;
  `git status` after every run. Trio BEFORE PR open.

## Test approach

- `pytest` directly; `./scripts/core/ci-check.sh` before pushing.
- F1: read-both tests from both paths; F2: export characterization;
  F3: desync fixture; F4: table-driven conformance incl. duplicates;
  plus the module-skip grep after every move batch.

## Evaluation summary

`arch-review-fast`: REVISION_SUGGESTED — one finding (abstract the
`.claude/` prefix), DECLINED: that path is Claude Code's own discovery
contract, an external interface not a brandable choice; the ADR's
harness-change revisit trigger covers it. Plan judged "exceptionally
sound". Disposition in the task file; log:
`.adversarial/logs/KIT-0057-canonical-homes-and-prune--arch-review-fast.md`.
No outstanding blockers.

## Out of scope

- Executing any 0.9.0-pinned removal (KIT-0047/0054/F1's — they
  execute IN 0.9.0)
- The plugin repo (file follow-ups only), downstream repos
- KIT-0051/0052/0055

## PR sizing

Single PR preferred (< 550 lines; the moves dominate). If the skills
merge balloons, split guards+prune (PR 1) from merge+docs (PR 2) —
pre-approved. Branch `feature/KIT-0057-canonical-homes-prune` (already
created).
