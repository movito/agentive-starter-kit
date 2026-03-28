# ASK-0043 Review Starter

**PR**: #40
**Branch**: `feature/ASK-0043-root-resolution-preamble`
**Commits**: 3 (feat + bot fixes + evaluator)

## What Changed

Added standardized root-resolution preamble to all 11 shell scripts so they
work from any subdirectory, not just the project root. Also fixed incorrect
depth (`..` -> `../..`) in 3 scripts broken by the v0.4.0 restructure.

## Files to Review (by priority)

1. **scripts/local/bootstrap.sh** — Most complex change. Renamed `ASK_ROOT` -> `PROJECT_ROOT`. Resolves TARGET to an absolute path before any directory changes, then uses absolute `$PROJECT_ROOT/...` paths for rsync sources (no `cd "$PROJECT_ROOT"` needed). Later does `cd "$TARGET"` for git init.

2. **scripts/core/verify-ci.sh** — Added `SELF` absolute path for `exec` re-invocation (was `exec "$0"` which breaks with relative paths after `cd`).

3. **scripts/core/ci-check.sh** — Preamble at top replaces local SCRIPT_DIR inside pattern lint step.

4. **Other 8 scripts** — Mechanical: add 3-line preamble after shebang. Scripts without `set -e` get `|| exit 1` on `cd`.

## Bot Review Summary

- **BugBot**: 2 real bugs found and fixed (bootstrap relative path, verify-ci exec)
- **CodeRabbit**: Approved after round 2. 4 `|| exit 1` guards added.
- **Evaluator**: 2 false positives (missed `set -e` from excerpted input)

## What to Verify

- [ ] `cd tests && ../scripts/core/ci-check.sh` works
- [ ] `cd tests && ../scripts/core/gh-review-helper.sh help` works
- [ ] `./scripts/core/ci-check.sh` still works from root
- [ ] bootstrap.sh TARGET resolution order is correct (resolves before cd)
