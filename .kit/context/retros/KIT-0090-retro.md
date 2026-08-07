## KIT-0090 — Extract the lifecycle scripts into the agentive-kit package (PRs #108–#111)

**Date**: 2026-08-07
**Agent**: feature-developer (f5)
**Mode**: single-repo
**Scorecard**: 40 threads (16+8+9+7), ~1 regression (membership-justification class), ~11 bot fix rounds, 27 commits (12+4+7+4) — aggregated across the 4-PR stack; `agentive-kit 0.1.0` published to PyPI at close

### What Worked

1. **Evaluator trio BEFORE PR open, with disposition records** — the pre-open rounds caught the two best bugs of the series before any human or bot saw them: the partial-ID substring match (`KIT-1` silently moving KIT-1234's file) and the packaged-checks exec-bit loss under pip/sdist installs. The per-PR disposition tables in `.kit/context/reviews/KIT-0090-pr{1..4}-evaluator-review.md` then made refuting repeat/oscillating findings a one-line citation instead of a re-investigation.
2. **Delegation with inline fallbacks preserved every consumer** — the pattern (package canonical → in-repo source → inline legacy fallback) kept the 1,033-test suite, the door E2E tests, and package-less consumer repos green through the whole extraction. The one time I skipped the fallback (PR 2's doctor), the dispatched CI run caught door-made consumers breaking within the hour.
3. **Mutation-testing the new guards** — deliberately breaking the KIT-0086 single-writer guard and the root-discovery rule and watching the right tests fail (3 each) proved the guard tests were live, not decorative. Cheap, high confidence.
4. **Programmatic extraction over retyping** — slicing function blocks out of `scripts/core/project` with Python scripts (then byte-parity tests for the copied check set) meant zero transcription drift across ~1,100 extracted lines.
5. **Manual `workflow_dispatch` as the standing CI proof** — with `pull_request` events dead (see below), dispatched runs on the branch became the merge-gate evidence, stated explicitly in every merge-go.

### What Was Surprising

1. **o3 reversed its own instructions twice** — round 4 demanded underscore block the ID boundary; round 5 called that same block a data-stranding regression. PR 4's round demanded generic `ImportError` catching that PR 1's round had explicitly forbidden. Verify-then-disposition (with the records as evidence) handled it; chasing verdict-green would have looped forever.
2. **`pull_request` events produced ZERO CI runs on all four PRs while stacked or freshly opened — but fired normally after retarget-to-main** (#109's retarget push triggered a real run). The anomaly is narrower than "pull_request is broken": it correlates with non-default bases at open time.
3. **The pytest-fast hook has a structural blind spot** — it deselects the slow door-E2E tests, so PR 2's doctor delegation passed every local gate and broke door-made consumers only in the dispatched full run. The fast hook is a commit-latency tool, not a merge gate.
4. **Worktree clones here have a narrow fetch refspec (`main` only)** — bare `--force-with-lease` fails with "stale info" because no remote-tracking ref exists for feature branches. Explicit-lease pushes (`--force-with-lease=<branch>:<exact-sha>` from `git ls-remote`) are the working pattern.
5. **CI's Python 3.10 job cannot represent bare 3.10** — pytest transitively installs `tomli`, so the tomllib-less code path only exists under `uv tool install`. BugBot's "missing tomli fallback" was real precisely where CI couldn't see it; closed with a forced-fallback test that blocks both modules via `sys.modules`.

### What Should Change

1. **Full-suite rule for delegation changes** — any change to how `scripts/core/project` resolves/delegates commands must run the FULL suite (not the fast hook) before push. One sentence in `TESTING-WORKFLOW.md`; it would have caught the PR-2 door break locally.
2. **The pull_request CI anomaly needs an owner** — it has now cost dispatch-babysitting across two task cycles (KIT-0067, KIT-0090). Propose a task: reproduce with a trivial PR, compare `branches:` filters vs. stacked-base opens, and either fix the trigger or bake the dispatch step into the feature-developer workflow.
3. **Worktree provisioning should widen the fetch refspec** (or the docs should teach the explicit-lease push). Extending `55-worktree-provisioning.sh` to WARN on a narrow refspec closes it as a doctor check (see Incident Closure).
4. **The deferred bash-port PR needs a planner sizing call** — preflight / review-input / worktree-lib (~1,370 bash lines) were deliberately split out of PR 3 (flagged in #110). Own task recommended: it is a rewrite with its own test-contract questions, not an extraction.
5. **Consider a deep-evaluator round cap in the workflow docs** — two documented oscillations suggest diminishing returns after ~2 deep rounds per PR; the disposition-table pattern (stop, record, cite) should be the named procedure.

### Permission Prompts Hit

1. `git push --force-with-lease origin feature/KIT-0090-doctor-migration` — denied by the permission layer (the documented STACKED-PR-WORKFLOW gotcha). Resolved by handing the operator explicit-lease commands via the `!` prefix; blocked ~minutes each time across three retargets. Deliberately not in the allow list (force-push should stay operator-gated) — but the *documented fallback* (branch replacement) is worse than the `!`-prefix relay used here; the workflow doc should name the relay as the preferred fallback.
2. An early `cd`-chained scratchpad command was denied once (compound `cd && rm` in the scratchpad); worked around immediately with absolute paths. Not allowlist-worthy.

### Process Actions Taken

- [ ] Add the full-suite-after-delegation-change rule to `TESTING-WORKFLOW.md`
- [ ] File the pull_request-CI-anomaly reproduction task (owner: planner)
- [ ] Extend `55-worktree-provisioning.sh` with a narrow-refspec WARN; add the explicit-lease push pattern to `WORKTREE-WORKFLOW.md` / `STACKED-PR-WORKFLOW.md`
- [ ] Planner sizing call on the deferred bash-port PR (preflight/review-input/worktree lib)
- [ ] Name the disposition-table procedure + deep-round cap in the review workflow docs
- [ ] Planner: close KIT-0086 and KIT-0079 by reference; update `agent-handoffs.json` on main at completion

### Incident Closure

1. **pull_request events produce no CI runs (stacked/fresh PRs)** — triage-guide entry: extend the `STACKED-PR-WORKFLOW.md` CI-gotcha section to cover the pre-retarget case (symptom: no run in `gh run list` after open/push; cause: correlation with non-default base; remedy: `gh workflow run test.yml --ref <branch>` is the proof). Not cheaply doctor-checkable (requires Actions history analysis); the reproduction task above pursues the root cause.
2. **Narrow fetch refspec breaks `--force-with-lease`** — doctor check: extend `55-worktree-provisioning.sh` to WARN when `remote.origin.fetch` covers only `main` (cite this incident in the check header). Action item filed above.
3. **Fast-hook blind spot (door E2E deselected)** — triage-guide entry in `TESTING-WORKFLOW.md` (the full-suite rule above); not a doctor concern (test-selection process, not environment).
4. **Bare-3.10 tomli masking in CI** — closed by regression test: `test_regex_fallback_rejects_non_string_pin` forces the no-TOML-module path via `sys.modules`, making the CI-invisible environment permanently visible to the suite.
