# KIT-0044 Review Starter — Worktree-Based Implementation Sessions

**PR**: https://github.com/movito/agentive-starter-kit/pull/76
**Branch**: `feature/KIT-0044-worktree-sessions` (worktree: `../ask-worktrees/KIT-0044`)
**Task**: `.kit/tasks/4-in-review/KIT-0044-worktree-based-implementation-sessions.md`
**Date**: 2026-07-14
**Agent**: feature-developer-f5 (second worktree pilot — self-demonstrating task)

## What shipped

| Req | Deliverable |
|-----|-------------|
| F1 | `scripts/local/new-worktree.sh` — create from fresh `origin/main`, enumerated provisioning list (`.venv`, `.env`, `.adversarial/evaluators` symlinks), sources pre-flighted before creation, refuses on existing path/branch/multiple specs/bare primary/missing origin-main |
| F2 | `TASK-STARTER-TEMPLATE.md` 1.1.0 — un-skippable LAUNCH block above FIRST ACTIONS; first action is branch-verify |
| F3 | Lifecycle in `WORKTREE-WORKFLOW.md` — session leaves worktree clean; planner removes post-retro |
| F4 | `.kit/context/workflows/WORKTREE-WORKFLOW.md` — topology, creation, GIT_DIR contract + canary, closeout; linked from CLAUDE.md |
| F5 | Bare-hub decision record in the doc — declined at current scale, 3 revisit triggers |
| — | `.gitignore`: `.adversarial/evaluators` (no trailing slash) so the provisioning symlink is ignored — keeps `git worktree remove` working without `--force` |
| — | `prepare-review-input.sh` 1.5.1 — dead `ADVERSARIAL_UNATTENDED` hint replaced with the working `echo y \|` pattern |

## Review state

- **CI**: green (lint, tests 418 passed / 92.6% coverage)
- **Bots**: BugBot pass (0 findings); CodeRabbit CHANGES_REQUESTED → 3 threads all fixed in `23c2e8f` → **APPROVED**; 3/3 threads resolved with replies
- **Evaluators** (run BEFORE PR, doc-dominated rule): fast-v2 CONCERNS / o3 CONCERNS / claude-code APPROVED — 4 accepted, 9 declined with evidence, incl. 2 disproven o3 claims. Disposition: `.kit/context/reviews/KIT-0044-evaluator-review.md`
- **Preflight**: 6/7 before this file existed; Gate 6 satisfied by this starter

## Verification highlights

- Helper exercised live from inside a worktree: symlinks resolve to the primary (common-dir logic verified)
- Scratch cycle: create → 419 tests collect → adversarial CLI lists evaluators → refusals (path/branch/bad-ID/no-spec/multi-spec) all exit 1 → empty-commit pre-commit run → **canary green** (`core.bare=false` in primary after every pre-commit run this session)
- Plain `git worktree remove` verified to work once symlinks are gitignored (isolated-repo experiment); worktrees created before this PR merges still need `--force`

## Reviewer attention points

1. `scripts/local/` placement (N3 default) — argued in the PR body; a `project worktree` subcommand would ship a bigger contract downstream
2. The bare-hub decision record (F5) — confirm the revisit triggers match planner expectations
3. `prepare-review-input.sh` is `scripts/core/` (synced downstream) — version bumped 1.5.0 → 1.5.1, no manifest count change

## Post-merge planner actions

- Remove this worktree after reading the retro: `git worktree remove ../ask-worktrees/KIT-0044` (may need `--force` — created pre-fix)
- `./scripts/core/project complete KIT-0044`
- Retro: `.kit/context/retros/KIT-0044-retro.md`
