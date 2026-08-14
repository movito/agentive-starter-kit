# KIT-ADR-0012: Task Status ↔ Linear Alignment

**Status**: Accepted

**Date**: 2025-11-28

**Deciders**: planner, User

## Context

### Problem Statement

Task files have a `**Status**:` field and live in numbered folders (`1-backlog/`, `2-todo/`, etc.). When syncing to Linear, we need clear rules for:

- Which status value to use
- How to handle conflicts between field and folder
- What to do with legacy status values
- When to exclude tasks from sync

This ADR documents the **implementation pattern** for status alignment. For the strategic decision on why we use custom sync (vs Linear MCP), see KIT-ADR-0003.

### Forces at Play

**Technical Requirements:**

- Status field and folder should both be valid indicators
- Legacy statuses from migrations must be handled
- Archive/reference folders should not sync
- Status must map to Linear's workflow states

**Constraints:**

- Linear has fixed workflow states (Backlog, Todo, In Progress, etc.)
- Files may have outdated status values
- Folder moves should update status

**Assumptions:**

- Git-tracked files are source of truth
- Linear is for team visibility, not primary editing
- Agents work with file-based task specs

## Decision

We will use a **3-level priority system** for status resolution, with automatic migration of legacy values.

### Core Principles

1. **Status field wins** (if Linear-native)
2. **Folder determines status** (if field missing/invalid)
3. **Default to Backlog** (if both unknown)
4. **Auto-migrate legacy** (update files during sync)

### Implementation Details

**Linear-Native Status Values (case-sensitive):**

| Status | Linear State | Description |
|--------|--------------|-------------|
| `Backlog` | Backlog | Planned, not started |
| `Todo` | Todo | Ready to be worked on |
| `In Progress` | In Progress | Currently being worked on |
| `In Review` | In Review | Awaiting review/approval |
| `Done` | Done | Completed successfully |
| `Blocked` | Blocked | Waiting on dependencies |
| `Canceled` | Canceled | Abandoned/not doing |

**Folder → Status Mapping:**

| Folder | Status | Synced? |
|--------|--------|---------|
| `1-backlog/` | Backlog | ✅ Yes |
| `2-todo/` | Todo | ✅ Yes |
| `3-in-progress/` | In Progress | ✅ Yes |
| `4-in-review/` | In Review | ✅ Yes |
| `5-done/` | Done | ✅ Yes |
| `6-canceled/` | Canceled | ✅ Yes |
| `7-blocked/` | Blocked | ✅ Yes |
| `8-archive/` | - | ❌ Excluded |
| `9-reference/` | - | ❌ Excluded |

**Status Resolution Priority:**

```text
┌─────────────────────────────────────────────────────┐
│  Priority 1: Status Field (if Linear-native)       │
│  ─────────────────────────────────────────────      │
│  **Status**: Todo  →  Use "Todo"                   │
│  **Status**: In Progress  →  Use "In Progress"    │
└─────────────────────────────────────────────────────┘
                        ↓ (if missing or invalid)
┌─────────────────────────────────────────────────────┐
│  Priority 2: Folder Location                        │
│  ─────────────────────────────────────────────      │
│  delegation/tasks/2-todo/TASK-001.md  →  "Todo"    │
│  delegation/tasks/5-done/TASK-002.md  →  "Done"   │
└─────────────────────────────────────────────────────┘
                        ↓ (if unknown folder)
┌─────────────────────────────────────────────────────┐
│  Priority 3: Default                                │
│  ─────────────────────────────────────────────      │
│  Unknown folder or missing status  →  "Backlog"   │
└─────────────────────────────────────────────────────┘
```

**Legacy Status Migration:**

When sync encounters non-Linear-native status values, it automatically updates the file:

| Legacy Value | Migrated To | Notes |
|--------------|-------------|-------|
| `draft` | `Backlog` | Planning phase |
| `planning` | `Backlog` | Planning phase |
| `ready` | `Backlog` | Waiting to start |
| `in_progress` | `In Progress` | Case normalization |
| `review` | `In Review` | Review phase |
| `testing` | `In Review` | Grouped with review |
| `completed` | `Done` | Completion synonym |
| `blocked` | `Blocked` | Case normalization |

**Migration behavior:**

```text
Before: **Status**: draft
After:  **Status**: Backlog
        (file is updated, then synced)
```

**Implementation (Python):**

```python
# scripts/linear_sync_utils.py

LINEAR_NATIVE_STATUSES = {
    "Backlog", "Todo", "In Progress",
    "In Review", "Done", "Blocked", "Canceled"
}

FOLDER_STATUS_MAP = {
    "1-backlog": "Backlog",
    "2-todo": "Todo",
    "3-in-progress": "In Progress",
    "4-in-review": "In Review",
    "5-done": "Done",
    "6-canceled": "Canceled",
    "7-blocked": "Blocked",
}

def determine_final_status(status_field: str, task_file: Path) -> str:
    """Resolve status using 3-level priority."""
    # Priority 1: Status field (if Linear-native)
    if status_field and status_field in LINEAR_NATIVE_STATUSES:
        return status_field

    # Priority 2: Folder location
    folder_status = determine_status_from_path(task_file)
    if folder_status:
        return folder_status

    # Priority 3: Default
    return "Backlog"
```

**Sync Exclusion Rules:**

```python
def should_sync_task(task_file: Path) -> bool:
    """Determine if task should be synced."""
    folder = get_folder_from_path(task_file)

    # Exclude archive and reference folders
    if folder in ["8-archive", "9-reference"]:
        return False

    return True
```

**Status Flow Diagram:**

```text
                    ┌──────────────────┐
                    │   Task File      │
                    │ (Source of Truth)│
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Status Check    │
                    │ (3-level priority)│
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼────┐  ┌──────▼──────┐  ┌────▼────────┐
     │ In Workflow │  │ Archive/Ref │  │   Legacy    │
     │   Folder    │  │   Folder    │  │   Status    │
     └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
            │                │                │
     ┌──────▼──────┐         │         ┌──────▼──────┐
     │ Sync to     │         │         │  Migrate    │
     │ Linear      │         │         │  Status     │
     └─────────────┘         │         └──────┬──────┘
                             │                │
                      ┌──────▼──────┐  ┌──────▼──────┐
                      │   Skip      │  │ Update File │
                      │   Sync      │  │ Then Sync   │
                      └─────────────┘  └─────────────┘
```

## Consequences

### Positive

- ✅ **Deterministic**: Same file always produces same status
- ✅ **Folder-driven**: Moving files changes status intuitively
- ✅ **Self-healing**: Legacy statuses auto-migrate
- ✅ **Exclusion control**: Archive/reference folders don't pollute Linear

### Negative

- ⚠️ **File modification**: Migration updates files (may trigger commits)
- ⚠️ **Case sensitivity**: Status values must match exactly
- ⚠️ **One-way only**: Linear changes don't flow back to files

### Neutral

- 📊 **Folder discipline**: Users must use correct folder names
- 📊 **Status field optional**: Can be omitted if folder is correct

## Alternatives Considered

### Alternative 1: Folder-Only Status

**Description**: Ignore status field entirely, derive only from folder

**Rejected because**:

- ❌ Loses flexibility for edge cases
- ❌ Can't override folder with field when needed
- ❌ Some workflows need field-based status

### Alternative 2: Field-Only Status

**Description**: Ignore folder, derive only from status field

**Rejected because**:

- ❌ Loses intuitive folder organization
- ❌ No visual indication of status in file browser
- ❌ Must open file to see status

### Alternative 3: No Migration

**Description**: Fail on legacy status values instead of migrating

**Rejected because**:

- ❌ Breaks existing task files
- ❌ Requires manual updates for migration
- ❌ Poor user experience

## Tooling Support

### Helper Commands

The `./scripts/project` CLI provides commands to maintain status/folder alignment:

```bash
# Move task and update Status field atomically
./scripts/project move ASK-0001 done
./scripts/project move ASK-0002 in-progress

# Shorthand commands
./scripts/project complete ASK-0001    # → 5-done, Status: Done
./scripts/project start ASK-0001       # → 3-in-progress, Status: In Progress
./scripts/project block ASK-0001       # → 7-blocked, Status: Blocked

# Validate all tasks
./scripts/project validate             # Check all statuses match folders
```

### Pre-commit Validation

A pre-commit hook validates Status field matches folder location:

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: validate-task-status
      name: Validate task status matches folder
      entry: python scripts/validate_task_status.py
      language: python
      files: ^delegation/tasks/.*\.md$
```

**Behavior:**

- Blocks commits if Status doesn't match folder
- Shows specific files and expected values
- Suggests fix: `./scripts/project move <task-id> <status>`

### Recommended Workflow

1. **Moving tasks**: Use `./scripts/project complete ASK-0001` instead of `git mv`
2. **Bulk fixes**: Run `./scripts/project validate` to find mismatches
3. **Pre-commit**: Automatically catches misaligned status before commit

## Real-World Results

**Current implementation:**

- `scripts/linear_sync_utils.py` - Status mapping utilities
- `scripts/sync_tasks_to_linear.py` - Sync orchestration
- `scripts/validate_task_status.py` - Pre-commit validation
- `./scripts/project` CLI - Helper commands (move, complete, start, block, validate)

**Observed behavior:**

- Tasks sync with correct status on push
- Legacy statuses auto-migrate transparently
- Archive folders excluded as expected
- Pre-commit prevents misaligned commits

## Related Decisions

- KIT-ADR-0003: Custom Linear Sync vs MCP (strategic decision)
- KIT-ADR-0006: Agent Session Initialization (status updates during tasks)

## References

- Implementation: `scripts/linear_sync_utils.py`
- Sync script: `scripts/sync_tasks_to_linear.py`
- GitHub Actions: `.github/workflows/sync-to-linear.yml`
- Linear Workflow States: <https://linear.app/docs/workflow-states>

## Revision History

- 2025-11-29: Added tooling support (v1.1)
  - Added `./scripts/project move/complete/start/block` commands
  - Added `./scripts/project validate` command
  - Added pre-commit hook for status validation
  - Updated References section
- 2025-11-28: Initial decision (Accepted)
  - Documented 3-level priority system
  - Defined folder → status mapping
  - Established legacy migration rules

---

**Template Version**: 1.1.0
**Last Updated**: 2025-11-29
**Project**: agentive-starter-kit
