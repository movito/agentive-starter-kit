# ASK-0034: Clean the Template

**Status**: In Progress
**Priority**: medium
**Assigned To**: feature-developer
**Estimated Effort**: 1-2 hours
**Created**: 2026-02-24
**Target Completion**: 2026-02-25

## Related Tasks

**Related**: ASK-0036 (Expand reconfigure — complementary cleanup)

## Status History

- **Todo** (from initial) - 2026-02-24 15:10:00

## Overview

Remove starter-kit artifacts that shouldn't survive in downstream projects. The `delegation/tasks/5-done/` folder has 33 ASK-* and 1 KIT-* completed tasks from the starter kit's own development history. These clutter downstream projects that inherit from the template. Additionally, `SETUP.md` describes starter-kit setup (not relevant to downstream), `scripts/create-agent.sh` has branding, and `docs/agentive-development/` contains educational material that belongs in the starter kit's docs site, not in every downstream project.

**Context**: This was identified in the dispatch-kit tidy audit (`.agent-context/2026-02-24-starter-kit-tidy-list.md` in the dispatch-kit repo). These artifacts confused dispatch-kit's developers and would confuse any downstream project.

## Requirements

### Functional Requirements

1. **Archive completed tasks**: Move all 33 ASK-* and 1 KIT-* files from `delegation/tasks/5-done/` to `delegation/tasks/8-archive/`
2. **Remove SETUP.md**: Delete `SETUP.md` (downstream projects have their own README.md)
3. **Remove branding from create-agent.sh**: Remove line 4 ("# Part of Agentive Starter Kit (ASK-0033 v2)") from `scripts/create-agent.sh`
4. **Archive educational docs**: Move `docs/agentive-development/` to `docs/archive/agentive-development/`

### Non-Functional Requirements
- All existing tests must continue to pass
- No changes to any Python source code

## Implementation Plan

### Step 1: Archive completed tasks

```bash
# Create archive directory if needed
mkdir -p delegation/tasks/8-archive/

# Move all completed tasks
git mv delegation/tasks/5-done/ASK-*.md delegation/tasks/8-archive/
git mv delegation/tasks/5-done/KIT-*.md delegation/tasks/8-archive/
```

**Verify**: `ls delegation/tasks/5-done/` should be empty (or contain only non-task files).

### Step 2: Delete SETUP.md

```bash
git rm SETUP.md
```

### Step 3: Remove branding from create-agent.sh

Change line 4 in `scripts/create-agent.sh` from:
```
# Part of Agentive Starter Kit (ASK-0033 v2)
```
To:
```
# Agent creation automation script
```

### Step 4: Archive educational docs

```bash
mkdir -p docs/archive/
git mv docs/agentive-development/ docs/archive/agentive-development/
```

## Acceptance Criteria

### Must Have
- [ ] `ls delegation/tasks/5-done/` returns 0 ASK-*/KIT-* files
- [ ] `SETUP.md` does not exist at repo root
- [ ] `grep -r "Part of Agentive Starter Kit" scripts/` returns nothing
- [ ] `docs/agentive-development/` does not exist (moved to `docs/archive/`)
- [ ] All existing tests pass: `pytest tests/ -v`
- [ ] `delegation/tasks/8-archive/` contains the 34 archived task files

## Time Estimate

| Phase | Time |
|-------|------|
| Move/delete files | 15 min |
| Edit create-agent.sh | 5 min |
| Run tests, verify | 10 min |
| **Total** | **~30 min** |

## Notes

- This is mostly file moves and deletes — low risk
- No Python code changes, so TDD is not applicable
- The `8-archive/` folder is excluded from Linear sync
