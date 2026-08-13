# KIT-0104: Ship the door in the package — Implementation Handoff

**You are the feature-developer-f5. Implement this task directly. Do
not delegate or spawn other agents.**

> ## PR 2 ADDENDUM (2026-08-13, planner — read this FIRST if you are
> ## the PR 2 session)
>
> **PR 1 is MERGED** (#129, squash `ca11cd7`; planner deep-dive PASS;
> record: `.kit/context/reviews/KIT-0104-evaluator-review.md`, review
> starter `.kit/context/KIT-0104-REVIEW-STARTER.md`). You are a FRESH
> session — the PR 1 session was retired at ~500k tokens. Everything
> you need is in files; do not guess at PR 1 history beyond them.
>
> **What PR 1 shipped** (now on main): `agentive_kit/door/` — Python
> front owns parsing + matrix (sole owner) + preset chain +
> orchestration; engines run unmodified as packaged data from a staged
> faux kit root; `tests/test_door_data_sync.py` byte-pins the kit-tree
> ↔ package copies BOTH directions (edit both sides in the same
> commit or it fails). `bootstrap` is UNTOUCHED — that is your job.
>
> **PR 1 operator decisions you inherit** (recorded in the review
> starter — binding, do not re-open): adopt = packaged-mode (no
> kit-tree copies; legacy copy-adopt retires WITH your shim); preset
> home anchors `<target-parent>/agentive-config`
> (`AGENTIVE_KIT_CONFIG_DIR` overrides); `--design-materials` refused
> with a project-intake pointer; `adopt --no-kit` = rung 0.
>
> **PR 2 scope** (spec PR Plan item 2 — F2 help half, F3, F4):
> 1. `scripts/local/bootstrap` → thin `exec` shim into the package;
>    equivalent flags; help output deferred to the package (grep-proof
>    that no second matrix copy survives).
> 2. `agentive new --no-kit` — rung 0 from the `new` verb; mirror the
>    rung-0 tail semantics from `_orchestrate` (offers acknowledged
>    out loud, no record, no doctor).
> 3. File the shim-removal task AND the engine-consolidation
>    follow-up, both pinned to the next minor release, linked from
>    the PR.
> 4. The known-bigger part (PR 1 session's own flag):
>    `tests/test_bootstrap_shapes.py` and the sourced-function unit
>    layer of `tests/test_setup_door.py` get rewritten to pin the
>    packaged contract — characterize-first, then rewrite. If the PR
>    outgrows the review-surface budget (PR-SIZE-WORKFLOW): STOP and
>    report a split to the planner; do not push through.
>
> **Session topology (PR 2)**: worktree
> `/Users/broadcaster_three/Github/ask-worktrees/KIT-0104` (unchanged,
> real venv), branch `feature/KIT-0104-pr2-shim` — already created by
> the planner off merged main, upstream set. Verify, never create.
>
> The original handoff below remains valid for anchors and fences,
> EXCEPT: its anchors predate the merge — re-verify against main
> (`validate_combo` now ALSO lives in
> `packages/agentive-kit/src/agentive_kit/door/__init__.py:487`; the
> bash copy in `bootstrap` is what your shim retires).

**Date**: 2026-08-13
**From**: planner-f5  **To**: feature-developer-f5
**Task**: .kit/tasks/3-in-progress/KIT-0104-ship-the-door-in-the-package.md
**Status**: Ready
**Evaluation**: arch-review-fast REVISION_SUGGESTED (2026-08-13) — one
finding, dispositioned in the spec header (engine-consolidation
follow-up pinned to next minor release). Log:
`.adversarial/logs/KIT-0104-ship-the-door-in-the-package--arch-review-fast.md`.
The parent ADR was separately evaluated (o3 + claude-arch, 2026-08-13);
its findings are already baked into the spec's F2/F4. Don't
re-litigate either.
**Target Codebase**: This repo (single-repo mode)

## Session topology (read before anything else)

- **Worktree**: `../ask-worktrees/KIT-0104` (real per-worktree venv,
  provisioned by `new-worktree.sh`)
- **Branch**: `feature/KIT-0104-door-in-package` — created by the
  planner at authoring time. **Verify, never create**: if
  `git branch --show-current` prints anything else, STOP and ask.
  Never `checkout -b` in this session.
- **Multi-PR plan — the spec's `## PR Plan` is authoritative**: three
  sequential PRs to main (port → shim+flag → prose sweep with KIT-0094
  riding). PR 1 ships from this branch; PRs 2 and 3 get fresh branches
  off updated main — ask the planner to provision each worktree when
  you reach it (worktrees/branches are planner-authored; the
  never-create rule applies to every PR, not just the first).

## Mission

Move the setup door into the `agentive-kit` package as `agentive new`
/ `agentive adopt`. The spec's F1–F6 are authoritative; the PR Plan
section maps them onto the three PRs. Headlines:

- **Port, not rewrite** (F1): Python owns argument parsing and the
  shape × profile matrix from day one; the three engines
  (`scripts/local/engine-*.sh`) ship as packaged data scripts invoked
  by the Python front. Attempting a shell→Python engine rewrite in
  this task is scope creep — the follow-up task you will file covers
  it.
- **Single matrix owner, even in the interim** (F2): matrix legality
  lives ONLY in the Python front after PR 1. `bootstrap --help` must
  defer, not duplicate.
- **`new --no-kit` is in scope** (F4): the rung-0 flag for blank
  projects, API-completeness half of the port.

## Verified anchors (2026-08-13 — re-verify before relying)

- `scripts/local/bootstrap` — `validate_combo()` at ~lines 402–438 is
  the current single home of cross-flag legality (verified by read
  today; the ADR's cited 406–434 is the same function, minor drift).
  The `--no-kit applies to --adopt (single shape) only` guard is the
  line F4 relaxes for `new`.
- `packages/agentive-kit/pyproject.toml` — `[project.scripts]` at
  line 29; console name `agentive` → `agentive_kit.cli:main`;
  collision check + `akit` fallback documented at lines 30–34
  (verified by read today).
- `packages/agentive-kit/src/agentive_kit/` — existing modules
  include `cli.py`, `root.py`, `worktree.py`, `preflight.py` (listed
  today). Read `cli.py`'s dispatch pattern before adding subcommands —
  pattern reuse per the pre-implementation skill.
- Three engines: `scripts/local/engine-scaffold.sh`,
  `engine-materials.sh`, `engine-consumer.sh` (listed today).
- Consumer-record regions: `engine-consumer.sh` owns the
  KIT-LOCAL marker regions — read it before touching record writing;
  the door writes the kit-install record through it.
- Portability: stock macOS bash 3.2 + BSD userland;
  `bash32_heredoc_apostrophes` in `.kit/context/patterns.yml` — the
  engines are full of heredocs-in-`$( )`. UNVERIFIED beyond the
  pattern entry: re-check any engine you repackage against it.

## Test approach

- Existing door characterization: `tests/test_bootstrap_shapes.py`
  (flagless baseline + shape invariants) — these pin today's behavior;
  they must stay green through PR 1 (bootstrap untouched) and PR 2
  (shim must be behaviorally identical).
- New tests: subcommand dispatch (pattern: `tests/agentive_kit/
  test_cli.py`), the no-path-relationship assertion (spec AC 1 — the
  test must *assert* the absence of a kit checkout, not assume it),
  `new --no-kit` rung-0 shape, matrix-legality single-ownership.
- `./scripts/core/ci-check.sh` locally before every push; evaluator
  (code-reviewer tier per standing policy) before each PR opens.
- Falsification where the spec asks for it; grep proofs in PR bodies
  (matrix single-implementation, factory-clone prose class).

## Out of scope — do not touch

- `project-intake` agent (KIT-0105 — blocked on this task; leave it).
- The derived-brief fallback (KIT-ADR-0033 — sequenced later).
- Full shell→Python engine rewrite (the follow-up task's job).
- `.kit/tasks/1-backlog/KIT-0103` R2 (door detect-and-warn) — it rides
  AFTER this port; do not implement it mid-port.
- Discovered gaps → file in `.kit/tasks/1-backlog/` (you are in the
  kit repo; the escape hatch applies as-is).

## Process citations (cite, don't restate)

- Review-surface budget: `.kit/context/workflows/PR-SIZE-WORKFLOW.md`
  — either PR blowing the budget → STOP and report a further split.
- Self-churn circuit breaker: bot-triage SKILL — applies per PR.
- Commit protocol, testing, review-fix:
  `.kit/context/workflows/*.md` as usual.
- KIT-0094 rides PR 3 (its spec is the config authority; scope
  exclusions listed there).
