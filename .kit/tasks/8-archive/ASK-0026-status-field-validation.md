# ASK-0026: Status Field Validation and Helper Commands

**Status**: Done
**Priority**: high
**Assigned To**: feature-developer
**Estimated Effort**: 2-3 hours
**Created**: 2025-11-29

## Related Tasks

**Parent Task**: None
**Depends On**: ASK-0005 (Linear Sync Infrastructure)
**Blocks**: None
**Related**: ASK-0025 (Linear Sync Verification)

## Overview

Strengthen Status field handling to prevent sync issues. The Status field in task files is the source of truth, but we need tooling to ensure it stays in sync with folder locations.

**Why Valuable**: Prevents silent sync failures like ASK-0001 to ASK-0004 being stuck in "Todo" despite being in `5-done/` folder.

## Problem Statement

1. Moving files between folders doesn't update Status field
2. No validation that Status matches folder location
3. Easy to forget to update Status when completing tasks
4. Sync uses Status field, so mismatches cause stale Linear data

## Acceptance Criteria

### Must Have

- [ ] Add `./scripts/project move` command to move task AND update Status
- [ ] Add pre-commit hook to validate Status matches folder
- [ ] Hook warns on mismatch, allows override with flag
- [ ] Document commands in README and agent prompts

### Should Have

- [ ] `./scripts/project complete ASK-0001` shorthand for moving to done
- [ ] `./scripts/project status ASK-0001` shows current status and folder
- [ ] Hook auto-fixes simple mismatches (with confirmation)

### Could Have

- [ ] `./scripts/project validate` command to check all tasks
- [ ] Integration with task monitor daemon

## Implementation

### Helper Command: `./scripts/project move`

```bash
# Move task to new status folder and update Status field
./scripts/project move ASK-0001 done
./scripts/project move ASK-0001 in-progress
./scripts/project move ASK-0001 blocked

# Shorthand for common operations
./scripts/project complete ASK-0001    # → 5-done, Status: Done
./scripts/project start ASK-0001       # → 3-in-progress, Status: In Progress
./scripts/project block ASK-0001       # → 7-blocked, Status: Blocked
```

### Pre-commit Hook

```bash
# .pre-commit-config.yaml addition
- repo: local
  hooks:
    - id: validate-task-status
      name: Validate task status matches folder
      entry: ./scripts/validate_task_status.py
      language: python
      files: ^delegation/tasks/.*\.md$
      pass_filenames: true
```

### Validation Script

```python
# scripts/validate_task_status.py
FOLDER_STATUS_MAP = {
    "1-backlog": "Backlog",
    "2-todo": "Todo",
    "3-in-progress": "In Progress",
    "4-in-review": "In Review",
    "5-done": "Done",
    "6-canceled": "Canceled",
    "7-blocked": "Blocked",
}

def validate_task(file_path):
    # Extract folder and status
    # Return error if mismatch
    pass
```

## Success Metrics

- Zero status/folder mismatches in commits
- Helper commands used by agents consistently
- No more stale Linear data from status mismatches

## Notes

- Keep Status field as source of truth (explicit control)
- Folder is the "physical location", Status is the "logical state"
- Pre-commit validates they match, helper commands keep them in sync

---

**Template Version**: 1.0.0
**Created**: 2025-11-29
