## ASK-0044 — Builder/Project Separation via .kit/ Boundary (PR #41)

**Date**: 2026-03-30
**Agent**: feature-developer-v5
**Scorecard**: 46 threads, 0 regressions, 3 fix rounds, 12 commits

### What Worked

1. **Systematic merge safety audit before merging** — Grepping all runtime code paths (scripts, pre-commit hooks, CI workflows, tests, agents, commands, launchers) for three stale path patterns (`delegation/tasks/`, `.adversarial/`, `.agent-context`) caught zero runtime issues and gave confidence to merge a 100+ file rename PR.
2. **BugBot caught a real stale-path bug in `scripts/core/project`** — Lines 71, 134, 154 still referenced `.kit/delegation/tasks` (an intermediate path from the directory reorganization) instead of `.kit/tasks`. This would have broken `find_task_file()`, `move_task()`, and `validate_all_tasks()` at runtime.
3. **Batch thread triage at scale** — Processing 46 threads across 2 bots in a single `/triage-threads` pass, categorizing into fix/resolve groups, then replying and resolving all via GraphQL was efficient. All 46 threads resolved, zero left open.
4. **Single-PR approach for the rename** — Bundling all path changes into one PR (rather than splitting across multiple) prevented partial-migration states where some files referenced old paths and others referenced new ones.

### What Was Surprising

1. **`settings.local.json` false positives in grep** — Auto-generated permission allow-list entries in the gitignored `settings.local.json` contained old paths, triggering grep matches during the merge safety audit. Required manual verification that these weren't runtime code.
2. **Launcher `PROJECT_ROOT` derivation silently wrong** — When `launch` and `onboarding` moved from `agents/` (1 level deep) to `.kit/launchers/` (2 levels deep), the `dirname` only went up one level, making `PROJECT_ROOT` point to `.kit/` instead of the repo root. This wouldn't have caused an obvious error — it would have silently looked for files in the wrong directory.
3. **`verify-ci.sh` misses pull_request-triggered workflows** — The CI check script only looks at `push`-triggered workflows, but the Tests workflow triggers on `pull_request`. Had to fall back to `gh run list` to confirm all 5 runs were green.

### What Should Change

1. **Add a path-consistency smoke test** — A test that greps all shell scripts and Python files for known path constants (`.kit/tasks`, `.kit/context`, `.kit/adversarial`) and verifies they exist on disk. Would have caught the `scripts/core/project` stale path without waiting for BugBot.
2. **Launcher scripts should self-test `PROJECT_ROOT`** — Add a guard like `[[ -f "$PROJECT_ROOT/pyproject.toml" ]] || { echo "ERROR: PROJECT_ROOT resolution failed"; exit 1; }` so that `dirname` depth errors fail fast instead of silently resolving to the wrong directory.
3. **`verify-ci.sh` should check both push and pull_request events** — Currently only checks push-triggered workflows, missing the primary test workflow.

### Permission Prompts Hit

None. All commands used were within the allow list.

### Process Actions Taken

- [ ] Add path-consistency smoke test to test suite
- [ ] Add `PROJECT_ROOT` self-test guard to launcher scripts
- [ ] Update `verify-ci.sh` to check both push and pull_request workflow events
- [ ] Document `settings.local.json` as a known grep false-positive source in patterns.yml
