---
description: Show active tasks, recent events, and project progress
version: 1.0.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-02-27
created-by: "@movito with planner2"
---

# Status Dashboard

Show the current state of the project.

## Step 1: Scan task folders

```bash
echo "=== In Progress ===" && ls delegation/tasks/3-in-progress/ 2>/dev/null || echo "  (none)"
```

```bash
echo "=== Todo ===" && ls delegation/tasks/2-todo/ 2>/dev/null || echo "  (none)"
```

```bash
echo "=== In Review ===" && ls delegation/tasks/4-in-review/ 2>/dev/null || echo "  (none)"
```

```bash
echo "=== Blocked ===" && ls delegation/tasks/7-blocked/ 2>/dev/null || echo "  (none)"
```

## Step 2: Check recent activity

```bash
# Recent commits
git log --oneline -5
```

```bash
# Current branch
git branch --show-current
```

## Step 3: Check event bus (if dispatch-kit is installed)

```bash
dispatch status --since 2h $ARGUMENTS 2>/dev/null || true
```

```bash
dispatch log --since 2h 2>/dev/null || true
```

If the dispatch CLI is not available, the task folder scan from Step 1 provides the primary status view.

## Step 4: Report

Present a compact dashboard:

```text
## Project Status

**Branch**: [current branch]

| Status | Tasks |
|--------|-------|
| In Progress | [list or "none"] |
| Todo | [list or "none"] |
| In Review | [list or "none"] |
| Blocked | [list or "none"] |

**Recent commits**: [last 3-5 commit subjects]
```
