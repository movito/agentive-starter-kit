# ASK-0043: Add Root-Resolution Preamble to Shell Scripts

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 2-3 hours
**Created**: 2026-03-25
**GitHub Issue**: #37 (Part 2)

## Related Tasks

**Parent Task**: n/a
**Related**: ASK-0042 (scripts restructure — Part 1 of #37)

## Overview

Shell scripts in `scripts/core/` assume they're invoked from the project root (`cwd == repo root`). In monorepo setups, agents frequently `cd` into workspace subdirectories (e.g., `site/` for npm), causing relative script paths to fail.

**Context**: Reported in GitHub issue #37. Part 1 (subdirectory structure) was resolved by ASK-0042/v0.4.0. Part 2 (root-resolution) is still open.

**Reported by**: Downstream user in `moss-skolemusikkorps` project (Astro + Sanity monorepo). Also filed as movito/dispatch-kit#76.

## Requirements

### Functional Requirements
1. Every shell script in `scripts/core/` must resolve its own project root and `cd` into it before doing work
2. Scripts must work correctly whether invoked from repo root, a subdirectory, or via absolute path
3. The preamble pattern must be standardized across all scripts

### Preamble Pattern

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"
```

Note: `../..` because scripts live in `scripts/core/` (two levels deep).

## Implementation Plan

### Files to Modify

All shell scripts in `scripts/core/`:
- `ci-check.sh`
- `verify-ci.sh`
- `preflight-check.sh`
- `check-bots.sh`
- `gh-review-helper.sh`
- `check-sync.sh`

And `scripts/optional/`:
- `create-agent.sh`
- `setup-dev.sh`

And `scripts/local/`:
- `bootstrap.sh`

### Approach

1. Add the 3-line preamble after the shebang + header comments in each script
2. Remove any existing `cd` assumptions or relative path workarounds
3. Test from subdirectory: `cd tests && ../scripts/core/ci-check.sh`

## Acceptance Criteria

### Must Have
- [ ] All shell scripts in `scripts/core/` have root-resolution preamble
- [ ] Scripts work when invoked from any subdirectory
- [ ] No regressions — scripts still work when invoked from project root
- [ ] `scripts/optional/` and `scripts/local/` scripts also updated

## Lessons from Downstream

**dispatch-kit PR #64** solved a related problem for Python: `resolve_project_root()` in `detect.py` walks up from CWD looking for `.dispatch/`, parses `.git` gitlink files (worktree detection), and caches per-process. Key design choices:
- 5-step resolution order: cache → env var override → walk-up → gitlink parse → CWD fallback
- Env var escape hatch (`DISPATCH_PROJECT_ROOT`) for unusual layouts
- 49 tests (35 unit + 14 integration), including fake worktree scenarios

**The shell script preamble is simpler** — no worktree detection needed, just `BASH_SOURCE` → dirname → walk up to repo root. But the dispatch-kit PR shows that:
1. Testing from subdirectories matters (they had "shadow bus" bugs)
2. An env var override (`PROJECT_ROOT` or similar) is worth considering for edge cases
3. The preamble depth (`../..` vs `..`) varies by script location — `scripts/core/` needs `../..`, `scripts/optional/` also needs `../..`, but `scripts/local/` also needs `../..`

**dispatch-kit #76** is still open — this fix will apply to both repos once synced.

**adversarial-workflow PR #42** restructured scripts to `core/local/optional` and updated 56 file references. They hit "6/7 slash commands were broken" from stale paths. Confirms that path resolution fragility is a real downstream pain point.

## References

- GitHub issue: #37
- dispatch-kit issue: movito/dispatch-kit#76 (still open)
- dispatch-kit PR #64: Python-side root resolution (merged, good design reference)
- adversarial-workflow PR #42: Scripts restructure (merged, confirms downstream impact)
- Discovered in: `moss-skolemusikkorps` (Astro + Sanity monorepo)
