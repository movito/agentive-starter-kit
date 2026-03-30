# Agent Context System

This directory contains coordination files for the agentive development workflow.

## Contents

### `agent-handoffs.json`
Current state of all agents - who's working on what, task status, and handoff notes.

**Structure**:
```json
{
  "agent-name": {
    "status": "idle | in_progress | completed",
    "current_task": "TASK-XXXX or null",
    "task_started": "YYYY-MM-DD or null",
    "brief_note": "Short status update",
    "details_link": "path/to/task/file.md"
  }
}
```

### `current-state.json`
Project-wide state tracking - version, configuration, metrics.

### `workflows/`
Documented procedures for common operations:
- `COMMIT-PROTOCOL.md` - How to make commits
- `TESTING-WORKFLOW.md` - TDD process
- `AGENT-CREATION-WORKFLOW.md` - Creating new agents
- `ADR-CREATION-WORKFLOW.md` - Architectural decisions

### `templates/`
Templates for handoff documents and coordination files.

## Usage

### Checking Agent Status
```bash
cat .kit/context/agent-handoffs.json | jq '.["agent-name"]'
```

### Updating After Task Completion
Agents should update `agent-handoffs.json` when:
- Starting a new task
- Completing a task
- Encountering blockers
- Handing off to another agent

## File Naming Convention

For dated files in this directory:
```
YYYY-MM-DD-DESCRIPTION.md
```

Example: `2025-11-25-PROJECT-SETUP-COMPLETE.md`

---

**Documentation Version**: 1.0.0
