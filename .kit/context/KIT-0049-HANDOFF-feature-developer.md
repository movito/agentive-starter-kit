# KIT-0049 Handoff — feature-developer

**Task**: `.kit/tasks/4-in-review/KIT-0049-shape-scoped-sync.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-14 (planner-f5)
**Estimated effort**: 2–3 hours

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0049/`** — branch
`feature/KIT-0049-shape-scoped-sync`, fully provisioned. Run
`git pull --ff-only` first (the worktree was cut just before the locked
spec landed on main).

## Mission

Unlock updates for planning-shaped repos: replace KIT-0048's honest
refusal with manifest-intersection sync. Both architectural decisions
are LOCKED in the spec — implement, don't re-litigate:

1. **Single source = the consumer's manifest.** Intersect upstream
   entries with what `scripts/.core-manifest.json` records. Never
   introduce unrecorded files.
2. **Implicit trigger.** Read the shape via `_doctor_shape()`
   (`scripts/core/project:1264`). No flag; no P3 dependency.

## Verified runtime facts (planner, 2026-07-14)

- The KIT-0048 refusal guard lives in `cmd_sync` (grep `shape` in
  `scripts/core/project` — guard + `_doctor_shape` reader). Keep the
  malformed-shape branch (exit 2), replace the planning branch.
- `PLANNING_CORE` / `PLANNING_LOCAL` at `bootstrap-consumer.sh:171/187`
  are SEEDING lists — do not read them from sync; do not move them.
- The engine's frozen exit-code contract (0/1/2/3/4) and its report
  machinery (`SyncReport`, warnings/announcements) are the extension
  points — skipped-addition naming should ride the existing report,
  not a new channel.
- KIT-0048's e2e scratch pattern (`test_bootstrap_consumer.py` /
  planning scratch repos) gives you the fixture recipe for a
  planning-shaped consumer with a reduced manifest.

## Implementation guidance

- **Where the intersection lives — engine or wrapper — is your one
  design call.** State it in the PR. Planner's prior: the *wrapper*
  passes the consumer file-list to the engine (e.g. an
  `only=`/allowlist parameter the engine may already have via
  `--only`) — check whether `--only` semantics already fit before
  adding anything; if they do, this task is mostly wiring + tests.
- Characterization first: single-shape sync (incl. an upstream
  ADDITION arriving) must stay byte-identical.
- Skipped additions: name them via the report; a planning consumer
  reading the sync output must see what upstream has that they don't.
- The replaced-manifest pin: after a planning sync, assert the
  manifest's file list is unchanged (reduced), not upstream's.
- Wrapper exit codes: self-review item 8 binds; the KIT-0037
  convention comments in `cmd_sync` mark the reserved codes.

## Test approach

- **Ordering rule (all tasks)**: local tests green → evaluator trio →
  PR open. `git status` after every evaluator run.
- Extend `tests/test_project_sync.py` (the engine/wrapper suite with
  `_clean_git_env` patterns): planning-shape sync e2e, addition-skip
  naming, manifest preservation, single-shape characterization,
  malformed-shape refusal retained.
- `pytest` directly; `./scripts/core/ci-check.sh` before pushing.

## Evaluation summary

`arch-review-fast`: REVISION_SUGGESTED — its core objection (spec
punted architecture) was accepted and resolved by LOCKING both
decisions; the new-config-file suggestion was declined (the consumer
manifest already is the declarative record). Disposition + locked
decisions in the task file; log:
`.adversarial/logs/KIT-0049-shape-scoped-sync--arch-review-fast.md`.
No outstanding blockers.

## Out of scope

- Shape-aware UPSTREAM manifests / addition delivery for planning
  repos (v1 limitation, recorded; P3-era revisit)
- New shape-config files of any format
- P1/P3/P7 work; doctor changes; bootstrap seeding-list changes
- Downstream repos

## PR sizing

Single PR (< 300 lines): branch `feature/KIT-0049-shape-scoped-sync`
(already created).
