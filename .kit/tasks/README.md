# Task Management System

This directory contains all task specifications organized by status.

## Folder Structure

Tasks are organized in numbered folders that map to workflow stages:

| Folder | Status | Description |
|--------|--------|-------------|
| `1-backlog/` | Backlog | Tasks planned but not yet ready to start |
| `2-todo/` | Todo | Tasks ready to be worked on |
| `3-in-progress/` | In Progress | Tasks currently being worked on |
| `4-in-review/` | In Review | Tasks awaiting review or approval |
| `5-done/` | Done | Completed tasks |
| `6-canceled/` | Canceled | Tasks that were abandoned |
| `7-blocked/` | Blocked | Tasks waiting on dependencies |
| `8-archive/` | Archive | Historical tasks (not synced to Linear) |
| `9-reference/` | Reference | Templates and documentation (not synced) |

## Task File Format

All task files should follow the template in `9-reference/templates/task-template.md`.

### Required Fields

```markdown
# TASK-NNNN: Task Title

**Status**: [Backlog | Todo | In Progress | In Review | Done | Blocked | Canceled]
**Priority**: [critical | high | medium | low]
**Assigned To**: [agent-name]
**Estimated Effort**: X-Y hours/days
**Created**: YYYY-MM-DD
```

### Task Naming Convention

```
TASK-NNNN-short-description.md
```

- `TASK` - Default prefix (configurable in .env as TASK_PREFIX)
- `NNNN` - 4-digit sequential number (0001, 0002, etc.)
- `short-description` - Kebab-case description

Examples:
- `TASK-0001-project-setup.md`
- `TASK-0002-add-user-authentication.md`

## Workflow

### Creating a New Task

1. Copy template from `9-reference/templates/task-template.md`
2. Create file in `2-todo/` (or `1-backlog/` if not ready)
3. Fill in all required fields
4. Run evaluation (if configured): `adversarial evaluate <task-file>`

### Moving Tasks

Simply move the file between folders. The status in the file should match the folder.

**With Linear sync enabled**: Status updates automatically sync to Linear.

### Task Lifecycle

```
1-backlog → 2-todo → 3-in-progress → 4-in-review → 5-done
                  ↘ 7-blocked ↗
                  ↘ 6-canceled
```

## Linear Integration (Optional)

If Linear is configured, tasks sync automatically:

- File moves trigger status updates in Linear
- Status field in file takes priority over folder location
- Folders 8-archive and 9-reference are excluded from sync

### Status Mapping

| Folder | Linear Status |
|--------|---------------|
| 1-backlog | Backlog |
| 2-todo | Todo |
| 3-in-progress | In Progress |
| 4-in-review | In Review |
| 5-done | Done |
| 6-canceled | Canceled |
| 7-blocked | Blocked |

## Best Practices

1. **One task per file** - Keep tasks focused and atomic
2. **Clear acceptance criteria** - Define what "done" means
3. **TDD requirements** - Include test requirements in every task
4. **Time estimates** - Always estimate effort
5. **Dependencies** - Document what blocks or is blocked by this task

---

**Documentation Version**: 1.0.0
