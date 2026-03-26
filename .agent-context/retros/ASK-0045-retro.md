## ASK-0045 — Fix Linear Sync Import Paths (PR #38)

**Date**: 2026-03-25
**Agent**: feature-developer-v5
**Scorecard**: 7 threads, 0 regressions, 2 fix rounds, 2 commits

### What Worked

1. **Handoff file was precise and complete** — The `ASK-0045-HANDOFF-feature-developer-v5.md` nailed the root cause, listed all files to inspect, and provided exact verification commands. Zero investigation time needed.
2. **Bot triage caught a real fallback bug** — BugBot flagged `from core.logging_config` as unreachable in direct-execution mode. This was a genuine fix: replaced with stdlib `logging.getLogger` fallback that actually works.
3. **CI with venv exposed a hidden import** — Local pytest skipped `@requires_gql` tests, but CI's Python 3.12 venv had `gql` installed, revealing `sync_tasks_to_linear.py` also imported from the old `scripts.linear_sync_utils` path. Without CI, this would have shipped broken.
4. **`/babysit-pr` workflow was efficient** — Two cycles: first fixed 3 real findings (fallback imports, checkbox formatting), resolved 4 as out-of-scope. Second cycle confirmed clean. All 7 threads commented and resolved.

### What Was Surprising

1. **Pre-commit Black stash/restore loop** — When unstaged files exist, pre-commit stashes them, Black reformats staged files, pre-commit reports failure, then restores stash (reverting Black's fixes). The workaround is staging ALL files before committing. This cost ~10 minutes of debugging.
2. **Three broken imports, not one** — The task spec identified one import path (`logging_config`), but there were actually three: `logging_config` in both production files plus `linear_sync_utils` in `sync_tasks_to_linear.py`. The handoff could have enumerated all broken paths.
3. **BugBot `.env` path finding was technically correct but out-of-scope** — `Path(__file__).parent.parent / ".env"` resolves to `scripts/.env` after the restructure, not repo root. Pre-existing issue from v0.4.0, not introduced by this PR. Correctly triaged as won't-fix.

### What Should Change

1. **Handoff files should enumerate ALL broken imports** — The planner verified one import path but didn't grep for all `from scripts.` imports across the affected files. A simple `grep -rn "from scripts\." scripts/optional/` in the handoff investigation would have caught all three.
2. **Add pre-commit Black interaction to patterns.yml** — The stash/restore loop is a footgun. Document in `patterns.yml → testing → pre_commit_black_stash` that all files must be staged before committing when Black is a pre-commit hook.
3. **`pyproject.toml` deselect entries should be removed** — The task spec mentioned removing deselect entries if tests pass, but the task file in `3-in-progress/` should be moved to `5-done/` and deselect entries confirmed removed.

### Permission Prompts Hit

None. All commands were within the existing allow list.

### Process Actions Taken

- [ ] Move ASK-0045 task file from `3-in-progress/` to `5-done/`
- [ ] Remove `test_linear_sync.py` deselect entries from `pyproject.toml` (if still present)
- [ ] Add pre-commit Black stash interaction note to `patterns.yml`
- [ ] Consider adding grep-all-imports step to planner's handoff investigation checklist
