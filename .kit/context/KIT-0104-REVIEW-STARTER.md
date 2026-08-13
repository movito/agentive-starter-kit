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
