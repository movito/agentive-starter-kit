# KIT-0104 — Review Starter (PR 1 of 3: the port)

**PR**: https://github.com/movito/agentive-starter-kit/pull/129
**Branch**: `feature/KIT-0104-door-in-package`
**Status**: CI green (3.10/3.12/3.14 + lint), CodeRabbit APPROVED,
BugBot clean on head, 24/24 threads resolved, evaluator trio run
pre-PR (record: `.kit/context/reviews/KIT-0104-evaluator-review.md`).
**Task**: `.kit/tasks/3-in-progress/KIT-0104-ship-the-door-in-the-package.md`
(stays in-progress — PRs 2 and 3 remain; move to in-review at PR 3).

## What this PR is

`agentive new` / `agentive adopt` as package subcommands (KIT-ADR-0030
PR 1 of 3). Python front owns parsing + the shape × profile matrix
(single owner from day one) + preset chain + orchestration; the two
engines run UNMODIFIED as packaged data from a runtime-staged faux kit
root. `bootstrap` untouched (exec shim = PR 2).

## Where to spend review attention

1. `agentive_kit/door/__init__.py` (~1.7k lines) — the port. The
   resolution chain and validate_combo mirror bootstrap; deviations
   are flagged inline with "deliberate deviation" comments.
2. The `--preserve-regions` hunk in `engine-consumer.sh` (both homes,
   byte-identical — the sync guard pins them).
3. `tests/test_door_data_sync.py` — the both-directions byte pin that
   makes the interim duplication safe. It caught real drift twice
   already (builder-only templates; main's v2.1.0 starter template).
4. The ~6.5k lines under `door/data/` are byte-identical copies —
   skimmable, sync-guard-pinned.

## Operator decisions baked in (2026-08-13, in-session)

- Adopt = packaged-mode (no kit-tree copies); legacy copy-adopt
  retires with the PR 2 shim, where test_bootstrap_shapes.py gets
  rewritten to pin the packaged contract.
- Preset home anchors to `<target-parent>/agentive-config`
  (AGENTIVE_KIT_CONFIG_DIR still overrides).
- `--design-materials` refused with a project-intake pointer;
  `adopt --no-kit` = rung 0 (no `.kit/`, no record).

## Review trail

- Pre-PR trio: fast (CONCERNS→fixed/refuted), o3 (FAIL→2 confirmed
  fixed, 2 hardened, 3 refuted with evidence), claude-code (largely
  confirmatory). Record has per-finding dispositions.
- Bot rounds: 1 real CI catch (PYTHONPATH for E2E subprocesses),
  1 sync-guard catch (upstream template v2.1.0), CodeRabbit's
  effective-pair finding CONFIRMED (latent in bash too) and fixed,
  2 BugBot decode/CRLF catches fixed. 15 doc-content findings on the
  byte-pinned copies → filed as KIT-0106 (pre-existing kit-doc
  defects, not introduced here).

## Next (planner)

- Merge gate: yours. After merge: provision PR 2's worktree/branch
  off updated main (shim + `new --no-kit` + the two follow-up tasks
  pinned to next minor), then PR 3 (prose sweep + KIT-0094).

---

# PR 2 of 3: the shim + `new --no-kit`

**PR**: https://github.com/movito/agentive-starter-kit/pull/130
**Branch**: `feature/KIT-0104-pr2-shim` (head `052ccac`)
**Status**: CI green (3.10/3.12/3.14 + lint) on head, CodeRabbit
APPROVED (latest review), BugBot pass, **8/8 threads resolved**,
preflight 7/7 PASS, evaluator trio run pre-PR (PR 2 section of
`.kit/context/reviews/KIT-0104-evaluator-review.md`).
**Task**: stays 3-in-progress by design — PR 3 (prose sweep +
KIT-0094 rider) remains.

## What this PR is

`scripts/local/bootstrap` → exec shim over the packaged door (execs
the checkout's own `packages/agentive-kit/src`; help defers; one
legacy branch, `--adopt --design-materials`, until KIT-0105);
`agentive new <dir> --no-kit` = rung 0 from the `new` verb; the two
pinned follow-ups filed (`1-backlog/KIT-0107` shim removal,
`1-backlog/KIT-0108` engine consolidation — both 0.10.0).

## Where to spend review attention

1. `scripts/local/bootstrap` (~190 lines) — the whole shim; the
   materials branch is the only behavior it owns.
2. `door/__init__.py` rung-0 generalization (~40 lines) — mkdir
   hoist + `if opts.no_kit:` branch + masking-class acks.
3. `tests/test_setup_door.py::TestShimStatic` — the F2 grep proof as
   a permanent test.
4. `tests/test_bootstrap_shapes.py::TestShimEquivalence` — the
   structural guarantee (tree-snapshot equality shim vs direct).

## Recorded decisions and deviations

- **Budget**: 832 additions / 3,263 deletions — over the 500 target;
  operator approved one PR in-session (2026-08-13): the shim breaks
  the legacy characterization instantly, so no green split lands
  under budget.
- **Deviations said out loud**: no TTY mode prompt in the shim (bare
  `bootstrap` → exit 2); `--design-materials` accepts no companion
  flags (fixed adopt/single/python); second mode flag refused
  (stricter-loud than the old last-wins).
- **Retirements riding the shim** (PR 1 operator decisions): legacy
  copy-adopt gone (adopt = packaged-mode); `--no-kit` = rung 0 both
  verbs (old seeded-record `--no-kit` gone).

## Bot rounds

Round 1: 7 threads (1 BugBot Medium — materials branch was missing
the old door's kit-root refusal, fixed `7971aef`; 6 CodeRabbit minor,
all fixed same commit). Round 2: 1 thread (equals-form targets get
the flag-value guard, fixed `052ccac`). Round 3: clean, CodeRabbit
APPROVED. Every thread replied + resolved.

## Next (planner)

- Merge gate: yours. After merge: provision PR 3's worktree/branch
  off updated main (prose sweep F5/F6 + KIT-0094 passenger; the
  CHANGELOG entry from this PR can be extended there).
- Deep-evaluator NOTE for your radar (dispositioned, not actioned):
  a root-anchored target (`agentive new /x`) resolves the preset home
  to `/agentive-config` — edge of the PR 1 target-parent anchor
  decision; seeding still requires the directory to already exist.

---

# PR 3 — the prose sweep (F5/F6 + KIT-0094 passenger), 2026-08-14

**PR**: https://github.com/movito/agentive-starter-kit/pull/131
**Branch**: `feature/KIT-0104-pr3-prose` (worktree ../ask-worktrees/KIT-0104)
**Status**: bots clean (round 2: CodeRabbit APPROVED + BugBot pass,
0 unresolved threads), tests/lint green on 3.10/3.12/3.14. FINAL PR
of the task.

## What shipped

- **KIT-0094 (passenger, complete)**: `.markdownlint-cli2.jsonc`
  (rule decisions recorded once, incl. MD029 `one_or_ordered` per
  KIT-0092 retro #6; scope = live markdown, `.coderabbitignore`
  precedent) + tree-wide pre-commit gate (`pass_filenames: false` —
  CLI paths extend config globs and bypass ignores, verified) +
  class sweep: ~1,150 violations / 95 files → 0 (199 files linted)
  + falsified once (planted bare fence → hook exit 1).
  **Acceptance observed, not assumed**: CodeRabbit's round 1 on this
  markdown-heavy PR produced ZERO markdown-style threads (its 7
  findings were all content, none lint) — the class is retired.
- **F5**: factory-clone precondition retired by class.
  STARTING-A-PROJECT teaches the sibling layout; README leads with
  `uv tool install agentive-kit && agentive new` (pipx named as
  alternative); `/new-project` + `/setup-preset` (both 1.3.0) derive
  from `agentive new --help`; config-home prose matches the packaged
  target-parent anchor everywhere (preset.example, doctor notes +
  packaged twins, `scripts/core/project` docstring). Grep proofs in
  the PR body; survivors are records + the optional guided-route
  session mechanics.
- **F6**: verified — no hardcoded flag list in either command
  (single `--no-preset` prose mention, present in help); pinned by
  `test_door_units.py::TestUsageText` (9 tests).
- Stale claims corrected while in there: adopt-copies caveat
  (packaged since PR 2), kit-clone `.env` carryover (the packaged
  door has none — `note_env_keys`), setup-preset config-home recipe
  off-by-one (pre-existing; recipe now verified live), playbook
  launcher policy unified (`.kit/launchers/launch` is the single
  survivor, KIT-0075).

## Bot rounds

Round 1: 8 threads (1 BugBot Medium — run-step/help-fallback
asymmetry in new-project.md, fixed `6a1be58`; 7 CodeRabbit — 5 fixed
same commit, 2 resolved-without-fix with reasons: plugin-release
coordination = planner-owned KIT-0096 post-merge, project-intake
door reference = KIT-0105/KIT-0107-F5 scope). Round 2: clean,
CodeRabbit APPROVED, BugBot pass. Every thread replied + resolved.

## Preflight

6/7 PASS. Gate 1 reads FAIL solely on the **Plugin Drift Guard** —
pre-existing red on main since 2026-08-12 (4 findings before this
PR; the sweep mechanically widens the list to 20). Tests pass.
Remedy is yours post-merge: cut the plugin release (KIT-0096
procedure) so it picks up the lint-clean bodies once. Precedent:
#129/#130 merged over the same red.

## Evaluator (Gate 5)

Fast-only per the prose-sweep exception (recorded in
`.kit/context/reviews/KIT-0104-evaluator-review.md`): FAIL verdict
refuted against the tree (the "conflicting ADR-0021 pair" is a
superseded-by-declaration pair from 2026-03; this PR only tagged
fences). The behavior-bearing hunks (lint config + hook) were
falsified live instead.

## Next (planner)

- **Merge gate: yours — this PR shape needs tree-grounded
  verification** (sectioned verifiers against the branch), per the
  prose-sweep rule. The trio was deliberately not the gate here.
- After merge: cut the plugin release (drift guard back to green),
  move KIT-0104 to 4-in-review/5-done (all three PRs landed),
  KIT-0094 can complete alongside (its acceptance evidence is in
  this starter), unblock KIT-0105.
