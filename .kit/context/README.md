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

Templates for handoff documents and coordination files:

- `review-starter-template.md` - copied by the `review-handoff` skill to
  create `<TASK-ID>-REVIEW-STARTER.md` (implementer → reviewer)
- `review-template.md` - used by the `code-reviewer` agent for its
  review output (reviewer → implementer)

### `archive/`

Handoffs, review starters, and session artifacts for tasks that have
reached a terminal folder (`5-done`, `6-canceled`, `7-blocked`,
`8-archive`), plus dated one-off session records. Frozen history —
read for precedent, never edit. Live coordination stays in this
directory's flat listing; when a task finishes, its artifacts move
here (KIT-0077).

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

```text
YYYY-MM-DD-DESCRIPTION.md
```

Example: `2025-11-25-PROJECT-SETUP-COMPLETE.md`

---

**Documentation Version**: 1.1.0
