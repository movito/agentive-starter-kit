# KIT-0092 — Review Starter

**PR**: https://github.com/movito/agentive-starter-kit/pull/118
**Branch**: `feature/KIT-0092-shim-removal` (worktree
`~/Github/ask-worktrees/KIT-0092`)
**Scope**: spec Parts A + C, released as **agentive-kit 0.3.1**. Part B
was already done (shipped in #116) and is untouched here.

## What this does

Removes the three one-release deprecation shims, sweeps every live
caller to the `agentive` CLI, and shrinks the test matrices that
existed to test them.

| Removed | Replacement |
|---|---|
| `scripts/core/preflight-check.sh` (76 lines) | `agentive preflight` |
| `scripts/core/prepare-review-input.sh` (65) | `agentive review-input` |
| `scripts/core/gh-review-helper.sh` (65) | `agentive review-helper` |

`scripts/core/project` and `scripts/local/new-worktree.sh` are
untouched — their clocks belong to phase 3 (spec Out of Scope).

## Gate status

- **Local suite**: 1185 passed / 13 skipped, full run incl. slow
  door-E2E, on the reviewed commit. Baseline before the change was
  1292/13 — the 107 delta is the dead bash parity cases, not lost
  coverage (see below).
- **Pre-commit gauntlet**: all hooks green, including the full
  pytest-fast guard (225 s).
- **Evaluator trio**: run BEFORE PR open (ordering rule). 2 FAIL, 1
  APPROVED — **nothing actioned**, because the two FAILs reviewed
  whole modules rather than the diff. Full reasoning + disposition
  table: `.kit/context/reviews/KIT-0092-evaluator-review.md`.
- **CI / bots**: pending push.

## What a human reviewer should actually look at

1. **The caller sweep was wider than the handoff's 8-file snapshot.**
   Beyond `.claude/`, the live surfaces were `scripts/.core-manifest.json`
   (3 entries), both ship lists in `engine-consumer.sh`, two `docs/`
   files, and — the one that would have shipped a real defect — the
   **package's own `--help`/usage strings**, which told users to run
   the very files this PR deletes. All three CLI help surfaces were
   run post-change to confirm they now print `agentive …`.
   Grep proving zero live references is in the PR body.

2. **The handoff's Part C table was wrong on two of four rows** —
   worth a planner glance. It earmarked `tests/test_project_script.py`
   (2,006 lines) and `tests/test_doctor.py` (2,645) for shrinkage, but
   neither file contains a single reference to the three removed
   shims; their bulk is `project`-shim and doctor coverage, both
   explicitly out of scope. ~4,650 lines were never in scope. Applied
   the handoff's own judgment rule ("nothing tests deleted code") to
   verified reality rather than to the predicted table. Operator
   confirmed this call mid-flight.

3. **Test shrinkage is parity-half removal, not scenario deletion.**
   The three matrices ran every scenario twice via
   `params=["bash","python"]`. The bash half died with the bash:

   | File | Lines | Cases |
   |---|---|---|
   | `test_preflight_check.py` | 1,215 → 1,174 | 84 → 42 |
   | `test_prepare_review_input.py` | 388 → 365 | 46 → 23 |
   | `test_gh_review_helper.py` | 339 → 319 | 42 → 21 |
   | **Total** | **1,942 → 1,858** | **188 → 94** |

   Every real scenario survives; no test body branched on `impl`, so
   the collapse touched only harness plumbing. Suite also got much
   faster (each bash case was a subprocess).

4. **Two harness details deliberately kept**, both verified against
   the source rather than assumed dead:
   - the `dispatch` PATH stub — `preflight._emit_dispatch_event` does
     `shutil.which("dispatch")` and shells out, and the module now runs
     **in-process**, so a real `dispatch` on a developer's PATH would
     otherwise be invoked for real by a test run;
   - `PREFLIGHT_CI_POLL_DELAY=0` — redundant with the `_sleep`
     monkeypatch, kept because it pins the seam the module documents.

   The `sleep` stub WAS removed (bash-only) and `bash` is still a
   genuine dependency of two harnesses because the canned-payload `gh`
   stub is itself a bash script.

5. **Shipset contract inverted, not dropped.** The three paths moved
   from `PLANNING_MUST_SHIP` to `PLANNING_MUST_NOT_SHIP` in
   `test_bootstrap_shapes.py`, and the seeded-manifest test now
   asserts their absence — a bootstrapped repo must neither receive
   them nor have `project sync` chase them.

6. **Loader-dedup decline from PR #113 is closed by deletion** — the
   duplication existed only while the shims did.

## Known-not-done (deliberate)

- **Downstream projects still calling the `.sh` paths must migrate**
  to the CLI (`uv tool install agentive-kit`). Flagged in the
  CHANGELOG under Removed.
- Every evaluator finding was dispositioned rather than fixed; the
  actionable ones are pre-existing module behavior deserving their own
  task (Gate 3 `completed:skipped`, Gate 1 event filter, path-escape
  hardening, `OSError` on write). See the review record.
- **Adjacent defect found while dogfooding, not fixed**: `agentive
  review-input`'s "Next steps" hint advertises
  `ADVERSARIAL_UNATTENDED=1`, which does not exist in the installed
  `adversarial-workflow` tool — the exact class `self-review` lesson
  #10 records from KIT-0044. Harmless (unknown env var ignored) but a
  false runtime claim in shipped output. Worth a small task.
