# Linear Sync Behavior

Reference document describing how Linear issue synchronization works in this
project. Covers the folder-to-status mapping, status determination priority,
task monitor, and common commands.

**Version**: 1.0.0

## Overview

The project keeps task files as Markdown in `delegation/tasks/` and
synchronizes them to [Linear](https://linear.app) via the GraphQL API. Each
numbered subfolder maps to a Linear workflow state so that moving a file
between folders is equivalent to dragging a card across a Kanban board.

| Script | Purpose |
|--------|---------|
| `scripts/sync_tasks_to_linear.py` | Creates or updates Linear issues from task files |
| `scripts/linear_sync_utils.py` | Status mapping, metadata parsing, legacy migration |

The CLI wrapper `./scripts/project` exposes these through subcommands (see
**Common Commands** below).

## Folder-to-Status Mapping

Task files live under `delegation/tasks/<folder>/`. Each folder maps to a
Linear status (defined in `linear_sync_utils.FOLDER_STATUS_MAP`):

| Folder | Linear Status | Description |
|--------|---------------|-------------|
| `1-backlog/` | Backlog | Planned but not yet ready to start |
| `2-todo/` | Todo | Ready to start, dependencies met |
| `3-in-progress/` | In Progress | Actively being worked on |
| `4-in-review/` | In Review | Implementation complete, under review |
| `5-done/` | Done | Fully complete and verified |
| `6-canceled/` | Canceled | Will not be implemented |
| `7-blocked/` | Blocked | Temporarily blocked on a dependency |
| `8-archive/` | *Not synced* | Historical tasks (excluded from sync) |
| `9-reference/` | *Not synced* | Reference documentation (excluded from sync) |

## Status Determination Priority

The final Linear status is resolved via a three-level priority system
(implemented in `determine_final_status()`):

```text
Priority 1: Status field in the task file (if Linear-native)
    -> (missing or not native)
Priority 2: Folder location (mapping table above)
    -> (folder not recognized)
Priority 3: Default to "Backlog"
```

**Linear-native status values** (case-sensitive):
`Backlog`, `Todo`, `In Progress`, `In Review`, `Done`, `Blocked`, `Canceled`

## Legacy Status Migration

Non-standard status values are auto-migrated by `migrate_legacy_status()`.
The migration permanently rewrites the `**Status**` field in the task file.

| Legacy Value | Migrated To |
|-------------|-------------|
| `draft`, `planning`, `ready` | Backlog |
| `in_progress` | In Progress |
| `review`, `testing` | In Review |
| `completed` | Done |
| `blocked` | Blocked |

## Task Monitor (Automatic Status Updates)

When the task monitor daemon is running it watches for file moves between
folders and automatically updates the `**Status**` field and syncs to Linear.

```bash
./scripts/start-daemons.sh           # Start all daemons (recommended)
./scripts/project daemon start       # Or start monitor individually
./scripts/project daemon status      # Check if running
./scripts/project daemon logs        # View activity
```

When the monitor is **not** running, folder moves do not update the status
field. Run `./scripts/project linearsync` to reconcile manually.

## Task File Format

Files must be named `PREFIX-NNNN-description.md` (e.g., `ASK-0037-workflow-verify-docs-only.md`).
Files in `8-archive/` and `9-reference/` are excluded from sync.

Metadata is extracted from bold-field notation:

```markdown
**Status**: In Progress
**Priority**: medium
**Assigned To**: feature-developer-v3
**Estimated Effort**: 2 hours
**Linear ID**: PRJ-42
```

The `**Linear ID**` field is auto-populated after the first sync.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LINEAR_API_KEY` | Yes | Personal API key from Linear settings |
| `LINEAR_TEAM_ID` | No | Team UUID or KEY (e.g., `AL2`). Auto-detects if omitted |

Set these in the project `.env` file. Obtain an API key at
`https://linear.app/{workspace}/settings/account/security`.

## Common Commands

### Sync all tasks to Linear

```bash
./scripts/project linearsync    # or: ./scripts/project sync
```

Scans folders `1-backlog/` through `7-blocked/`, parses every matching task
file, and creates or updates the corresponding Linear issue.

### Check sync status

```bash
./scripts/project sync-status
```

Compares local tasks against Linear issues and reports mismatches.

### Move a task between statuses

```bash
./scripts/project move ASK-0037 in-progress
./scripts/project start ASK-0037       # Shorthand: move to in-progress
./scripts/project complete ASK-0037    # Shorthand: move to done
./scripts/project block ASK-0037       # Shorthand: move to blocked
```

Moves the file to the correct numbered folder and updates `**Status**`.

### Other commands

```bash
./scripts/project teams       # List Linear teams (find LINEAR_TEAM_ID)
./scripts/project validate    # Check status fields match folders
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "gql package not installed" | `pip install 'gql[requests]'` |
| "LINEAR_API_KEY not found" | Add `LINEAR_API_KEY=lin_api_...` to `.env` |
| Mismatch detected by sync-status | Run `./scripts/project linearsync`, then `./scripts/project sync-status` |
| Status field disagrees with folder | Run `./scripts/project validate`, then move file or edit status |

## References

- ADR: `docs/decisions/starter-kit-adr/KIT-ADR-0012-task-status-linear-alignment.md`
- Planner agent: `.claude/agents/planner2.md` (Linear Sync section)
- Commit protocol: `.agent-context/workflows/COMMIT-PROTOCOL.md`
