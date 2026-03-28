# ASK-0043: Add Root-Resolution Preamble to Shell Scripts — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-03-28
**From**: Planner (planner2)
**To**: feature-developer-v5
**Task**: `.kit/delegation/tasks/2-todo/ASK-0043-root-resolution-preamble.md`
**Status**: Ready for implementation
**Evaluation**: Skipped (mechanical task, low risk, well-defined scope)

---

## Task Summary

Add a standardized root-resolution preamble to all shell scripts so they work
correctly when invoked from any subdirectory, not just the project root.

## Current Situation

Shell scripts in `scripts/core/` assume `cwd == repo root`. In monorepo setups,
agents frequently `cd` into workspace subdirectories (e.g., `site/` for npm),
causing relative paths to fail. Reported in GitHub issue #37 and dispatch-kit#76.

## Your Mission

Add this 3-line preamble after the shebang + header comments in every shell script:

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"
```

### Files to Modify (9 scripts)

**`scripts/core/`** (6 files — `../..` = two levels up):
1. `ci-check.sh`
2. `verify-ci.sh`
3. `preflight-check.sh`
4. `check-bots.sh`
5. `gh-review-helper.sh`
6. `check-sync.sh`

**`scripts/optional/`** (2 files — `../..` = two levels up):
7. `create-agent.sh`
8. `setup-dev.sh`

**`scripts/local/`** (1 file — `../..` = two levels up):
9. `bootstrap.sh`

**Note**: `wait-for-bots.sh` is also in `scripts/core/` — check if it needs the
preamble too. The task spec lists 6 core scripts but there are 7 `.sh` files.

### What NOT to modify

- `scripts/core/project` (Python script, already resolves its own root via `Path(__file__)`)
- `scripts/core/pattern_lint.py` (Python)
- `scripts/core/validate_task_status.py` (Python)
- `scripts/core/logging_config.py` (Python)

## Implementation Steps

1. For each script: add the preamble after shebang + any `set -e`/`set -o` lines
2. Remove any existing ad-hoc `cd` or relative path workarounds that the preamble replaces
3. Test from a subdirectory: `cd tests && ../scripts/core/ci-check.sh` (should work)
4. Test from project root: `./scripts/core/ci-check.sh` (should still work)

## Acceptance Criteria

- [ ] All 9 shell scripts have the root-resolution preamble
- [ ] Scripts work when invoked from any subdirectory
- [ ] No regressions when invoked from project root
- [ ] `./scripts/core/ci-check.sh` passes (this runs the full local CI check)

## Time Estimate

1-2 hours total:
- Adding preambles: 30 min
- Testing from subdirectory: 30 min
- CI verification: 30 min

## Starting Point

1. `grep -L 'SCRIPT_DIR' scripts/core/*.sh scripts/optional/*.sh scripts/local/*.sh` — find scripts missing the preamble
2. Check if any scripts already have partial root resolution to avoid duplication

---

**Task File**: `.kit/delegation/tasks/2-todo/ASK-0043-root-resolution-preamble.md`
**Handoff Date**: 2026-03-28
**Coordinator**: Planner (planner2)
