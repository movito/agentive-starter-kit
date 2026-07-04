## KIT-0036 — Pull-based consumer sync: engine + `project sync` (PRs #63 + #64)

**Date**: 2026-07-04
**Agent**: feature-developer
**Mode**: single-repo
**Scorecard**: 28 threads (15 on #63, 13 on #64), ~2 regressions (repeated within-task patterns), ~10 fix rounds, ~16 commits across 2 PRs

### What Worked

1. **Verify-before-believing on evaluator findings** — o3 (FAIL) urged recomputing `complete` from physically-synced files so a missing source file marks the sync partial. Declined because `test_core_manifest.py` CI-guarantees every source manifest entry exists on disk (so the case can't occur for a real kit), and the "fix" would have set *sticky* `partial_sync` from upstream anomalies. Reasoning captured in `.kit/context/reviews/KIT-0036-evaluator-review.md`. Roughly 8 of the o3/claude-code findings were accepted, but this one decline avoided a genuine regression.
2. **Full-plan-in-memory + two-pass temp-then-commit made self-overwrite provably safe** — the engine's own file is in `scripts_core`, so a real sync overwrites the running module. The design (read all source bytes+mode before the first write) plus a real-subprocess self-sync test (`TestSelfSyncSubprocess`) proved the running engine can overwrite itself end-to-end, not just in-process.
3. **`git rebase --onto origin/main <PR1-tip>` cleanly reconciled the stacked PR** after #63 was *squash*-merged — it dropped PR 1's now-redundant originals and the redundant #62 merge ("patch already upstream"), leaving a PR-2-only diff with zero conflicts.
4. **Pushing a fix commit to trigger CI** solved the base-retarget problem — a base change fires `pull_request: edited`, which doesn't trigger `test.yml` (wants `synchronize`). Bundling the next Cursor fix into a push ran CI naturally instead of a hacky empty commit or close/reopen.

### What Was Surprising

1. **The pre-commit `GIT_DIR` → `core.bare=true` gotcha** — pre-commit sets `GIT_DIR`/`GIT_WORK_TREE`; the new `test_project_sync.py` ran `git -C <tmp>` which inherited them, so operations leaked onto the *real* repo and flipped `core.bare=true`, breaking every subsequent `git add`/`commit` with "must be run in a work tree". Tests passed when run directly (no `GIT_DIR`), so it only bit under pre-commit — brutal to diagnose. Fixed with `_clean_git_env()` and documented in `TESTING-WORKFLOW.md`. Also a real `cmd_sync` robustness fix.
2. **CodeRabbit skips PRs whose base isn't the default branch** ("reviews are disabled for this base branch") — the stacked PR #64 got *no* CodeRabbit review until it was retargeted to `main`, which then surfaced 4 fresh findings. Worth knowing before stacking.
3. **The "exit 1 is reserved for drift" finding recurred 3×** — branch-checkout failure, then missing-engine import, both flagged separately by Cursor as returning `1` (drift) for a hard failure. Same principle, three findings across rounds.
4. **Preflight Gate 2 false-negatived again** (the open KIT-0034 F1) on a docs-only commit SHA — CodeRabbit check-run pass + last review APPROVED + 0 threads, but no review *event* on the exact SHA. Known, but recurred and cost a verification detour.

### What Should Change

1. **Fix preflight Gate 2 (KIT-0034 F1 is still open)** — it false-negatived again this task. Accept "CodeRabbit check-run pass + latest review APPROVED + 0 unresolved threads" as PASS instead of requiring a review event on the exact head SHA.
2. **Codify a wrapper exit-code convention** — self-review item: a wrapper around an engine with a frozen exit-code contract must not reuse the engine's reserved success/drift codes (0/1) for wrapper-level failures. Environment/precondition failures → exit 2. Three bot findings traced to this.
3. **Document the stacked-PR retarget-after-squash-merge flow** (`git rebase --onto origin/main <base-tip>`, then force-push + `gh pr edit --base main`, then a push to trigger CI). Non-obvious; derived live. Belongs in a PR-workflow doc next to `PR-SIZE-WORKFLOW.md`.
4. **Self-review checklist: staging must be scoped to changed paths** — the "stage whole roots / `git add -A`" issue recurred (workflow in PR 1, then `_stage_and_commit` in PR 2). Rule: in any sync/commit helper, stage the exact changed paths (from the report), never whole roots or `-A`, unless the tree is guaranteed clean.

### Permission Prompts Hit

- **`$()` subshell** in a smoke test (`TMP=$(mktemp -d)`) — denied immediately; split into fixed-path separate commands. Already a known gotcha in memory.
- **`rm -rf /tmp/... && mkdir ...`** compound — denied; ran as separate commands.
- **`git push --force-with-lease ...`** (for the rebase) — denied when issued in a `cd ... &&`-style compound; succeeded when re-issued as an isolated `git -C <path> push --force-with-lease`. ~1 retry.
- **`git branch -D kit0036-pr2-backup`** — denied; left the local backup branch in place (harmless).

None of these are in `.claude/settings.json` allow patterns; force-push and branch-delete are reasonably gated. The recurring lesson is to issue git/gh mutations as single isolated commands, not compounds.

### Process Actions Taken

- [ ] Fix preflight Gate 2 (KIT-0034 F1) — accept check-run + APPROVED + 0 threads
- [ ] Codify wrapper exit-code convention (reserved 0/1 only for engine semantics; precondition failures → 2) as a self-review item
- [ ] Document the stacked-PR retarget-after-squash-merge workflow
- [ ] Add self-review item: sync/commit staging scoped to changed paths, never whole roots / `-A`
- [x] Documented the pre-commit `GIT_DIR`/`core.bare` gotcha in `TESTING-WORKFLOW.md`
