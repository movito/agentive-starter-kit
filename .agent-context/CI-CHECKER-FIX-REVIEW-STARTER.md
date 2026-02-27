# Review Starter: ci-checker Bash Permission Bug Fix

**Task**: Fix ci-checker subagent Bash permission denial (reported by dispatch-kit)
**Branch**: fix/ci-checker-bash-permission-bug → main
**PR**: https://github.com/movito/agentive-starter-kit/pull/15

## Implementation Summary

The ci-checker agent's only tool is Bash, which gets denied when launched as a background subagent via the Task tool (no interactive user to approve the permission). All 3 agents that invoked ci-checker as a subagent were affected, wasting ~7.5k tokens per invocation with zero useful work.

The fix replaces all subagent invocations with direct calls to `./scripts/verify-ci.sh`, which already existed and does the same thing. The ci-checker agent is preserved for interactive use with a warning banner.

- Replaced Task tool ci-checker invocations in 3 agent docs with `./scripts/verify-ci.sh <branch> --wait`
- Updated COMMIT-PROTOCOL to remove "Option 1: ci-checker Agent" and unify on the script
- Fixed pre-existing issues: incorrect usage syntax, stale TIMEOUT status references
- Added "Interactive use only" warning to ci-checker.md
- Bonus: Fixed Black formatting divergence between Python 3.11 (CI) and 3.13 (local) in `sync_tasks_to_linear.py`

## Files Changed

### Modified Files
- `.claude/agents/ci-checker.md` - Added "Interactive use only" warning banner
- `.claude/agents/feature-developer.md` - Replaced ci-checker subagent invocation with `verify-ci.sh`; fixed Soft Block policy (TIMEOUT → IN PROGRESS/MIXED)
- `.claude/agents/planner.md` - Same replacements as feature-developer
- `.claude/agents/powertest-runner.md` - Same replacements; fixed 2 additional stale ci-checker references
- `.agent-context/workflows/COMMIT-PROTOCOL.md` - Removed ci-checker Option 1; fixed usage syntax to use `--wait`/`--timeout` flags; updated checklist references
- `scripts/sync_tasks_to_linear.py` - Black formatting alignment for Python 3.11 CI compatibility (no functional change)

### New Files
None

### Deleted Files
None

## Test Results

```
135 selected, 123 passed, 12 skipped, 9 deselected
All pre-commit hooks passed (Black, isort, flake8, pytest)
CI: Lint & Format Check ✅, Run Tests ✅
```

## Areas for Review Focus

1. **Consistency across agents**: Verify that the verify-ci.sh invocation pattern is consistent across feature-developer, planner, and powertest-runner — each had slightly different surrounding context
2. **Soft Block policy alignment**: The new IN PROGRESS / MIXED statuses should match what `scripts/verify-ci.sh` actually emits — verify against the script source
3. **COMMIT-PROTOCOL usage syntax**: The updated examples should match the script's actual `--wait` / `--timeout` flag interface
4. **Black formatting commit**: The `sync_tasks_to_linear.py` change is purely formatting (Python 3.11 Black vs 3.13 Black divergence) — verify no functional changes

## Related Documentation

- **Bug report**: `/Volumes/Macintosh HD/Users/broadcaster_three/Github/dispatch-kit/.agent-context/reports/ci-checker-bash-permission-bug.md`
- **Script source**: `scripts/verify-ci.sh` (unchanged, 224 lines)
- **Slash command**: `.claude/commands/check-ci.md` (unchanged, wraps verify-ci.sh)

## Pre-Review Checklist (Implementation Agent)

- [x] All acceptance criteria implemented (no more subagent invocations)
- [x] No new tests needed (documentation-only changes + formatting fix)
- [x] CI passes (PR #15, all checks green)
- [x] No debug code left behind
- [x] CodeRabbit review feedback addressed (4/4 findings fixed)

## External Review

- **CodeRabbit**: APPROVED (4 outside-diff findings addressed in follow-up commit)
- **BugBot**: No comments

---

**Ready for code-reviewer agent in new tab**

To start review:
1. Open new Claude Code tab
2. Run: `agents/launch code-reviewer`
3. Reviewer will auto-detect this starter file
