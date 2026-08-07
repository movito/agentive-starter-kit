# KIT-0091: Port the bash gate surfaces into agentive-kit (phase 1b)

**Status**: Todo
**Priority**: medium-high (completes phase 1's module list; blocks nothing in phase 2, but every day unported is a day the package and the shims tell different stories)
**Type**: Infrastructure / migration
**Estimated Effort**: 1-2 days (own PR series, likely 2 PRs)
**Created**: 2026-08-07
**Source**: KIT-0090 sequencing decision — raised in PR #110 rather than silently merged (correctly, per its handoff); planner sizing call 2026-08-07: own task, not a KIT-0090 continuation
**Evaluation**: arch-review-fast APPROVED 2026-08-07 after 1 revision round (`ghio` module accepted; parity-binds-behavior-not-shape clarified). Log: `.adversarial/logs/KIT-0091-port-gate-scripts--arch-review-fast.md`

## Overview

KIT-0090 shipped `agentive-kit` 0.1.0 with `gitio`, `lifecycle`,
`doctor`, and `evaluators` — but three surfaces from its F1 list were
deferred because they are a **rewrite, not an extraction** (~1,370
lines of bash whose Python equivalents did not exist):

- `scripts/core/preflight-check.sh` — the 7-gate completion check
- `scripts/core/prepare-review-input.sh` (+ `gh-review-helper.sh`) —
  review-input assembly, cross-repo aware
- the worktree LIBRARY half of `scripts/local/new-worktree.sh`
  (resolution + provisioning list; the door-side entry script stays
  for phase 2)

These are GATE code: preflight decides when a task may request human
review, and review-input feeds the evaluator gate. A parity bug here
doesn't fail loudly — it silently weakens the workflow's trust. That
is why this is a spec'd task with its own gates, not a tail on a
shipped one.

## Requirements

- **F1 — port each surface to a package module** (`preflight`,
  `review_input`, `worktree`) under the KIT-0090 house rules: typed
  models at boundaries, all git via `gitio`, no module > ~800 lines,
  per-module tests. All `gh`/GitHub interactions go behind a `ghio`
  module (the `gitio` pattern applied to the other CLI — one greppable
  home, testable via stubs; evaluation finding, accepted), and
  `review_input` depends on `ghio`, never on raw `gh` calls.
- **F2 — parity is the acceptance bar, proven not asserted.** For each
  surface, before the rewrite, capture the bash version's behavior on
  a fixture matrix (pass/fail/edge per gate; the KIT-0043 at-cap
  PENDING semantics for preflight Gate 1 explicitly). The Python port
  must reproduce the matrix; the matrix commits with the PR as the
  parity record. Divergences are allowed only as documented
  improvements, each named in the PR body. **Parity binds BEHAVIOR,
  not code shape** (evaluation finding, accepted): the matrix is the
  functional bar, and the port restructures freely behind it —
  Pythonic data structures, real error handling, no transliterated
  bash idioms; reproducing the old code's shape would defeat the
  point of the rewrite.
- **F3 — shims replace the bash bodies** (same one-release deprecation
  pattern as `project`); skills/commands that invoke these scripts
  (`preflight`, `check-bots`, review-handoff flow) keep working
  unchanged through the shims.
- **F4 — falsifiability discipline**: every ported gate test is broken
  once against its guarded condition (house rule). The stub-git and
  `GIT_*`-isolation fixtures apply.

## Acceptance Criteria

- [ ] Three modules in `agentive-kit`; parity matrices recorded and
      green for all three
- [ ] Shims in place; `/preflight` and the review flow work unchanged
      from a repo using only the installed package
- [ ] Existing suite green; new per-module tests; no monolith test
      files grow (they shrink)
- [ ] Released as agentive-kit 0.2.x

## Out of Scope

- Phase 2 (door switch) — including `new-worktree.sh`'s entry script
  and any `scripts/local/` change
- Behavior improvements beyond documented parity divergences
- wait-for-bots/check-bots scripts (they are thin `gh` wrappers; port
  only if trivially absorbed by review_input, else leave for phase 2)

## Notes

- KIT-0090's task file closes when this is filed (its disposition
  points here for the deferred slice); its retro is still owed by the
  implementing session before the planner removes the worktree.
