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
