# Shared Board & Artifact System Analysis

**Date**: 2026-02-05
**Research Phase**: 3 (Shared Board / Artifact System)
**Status**: Complete

---

## Executive Summary

Miriad uses a **hierarchical artifact system** within **channels** (boards/workspaces) where agents and humans collaborate on shared work products. Artifacts are versioned, typed entities with status-based workflows - conceptually similar to our task files but with richer metadata and real-time synchronization.

**Key Insight**: Their artifact model maps well to our file-based approach. We can adapt their type taxonomy and status workflows while using the filesystem as our persistence layer.

---

## Channel Model

Channels are the collaboration workspace - analogous to a project or feature scope.

### Channel Structure

```typescript
interface StoredChannel {
  id: string;
  spaceId: string;           // Multi-tenant isolation
  name: string;
  tagline?: string;          // Short description
  mission?: string;          // Detailed purpose
  archived: boolean;
  createdAt: Date;
  updatedAt: Date;
}
```

### Channel API

| Endpoint | Purpose |
|----------|---------|
| `GET /channels` | List all channels |
| `POST /channels` | Create new channel |
| `GET /channels/:id` | Get channel with roster |
| `PUT /channels/:id` | Update metadata |

### Channel Roster

Each channel has a **roster** - the list of active agents:

```typescript
interface RosterEntry {
  callsign: string;          // Agent's display name
  agentType: string;         // Agent definition slug
  status: RosterStatus;      // active | idle | busy | offline | paused | archived
  heartbeat: Date;           // Last activity
  runtimeId?: string;        // Bound runtime
}
```

**Status Flow**:
```
active ←→ idle ←→ busy
   ↓         ↓      ↓
paused ←→ offline → archived
```

---

## Artifact Type System

### Artifact Types (12 total)

| Type | Category | Purpose |
|------|----------|---------|
| `doc` | Content | General documentation |
| `folder` | Structure | Organize other artifacts |
| `task` | Workflow | Work items with status |
| `code` | Content | Code snippets/files |
| `decision` | Content | ADRs, design decisions |
| `knowledgebase` | Structure | Constrained to doc/folder children |
| `asset` | Binary | Images, files, attachments |
| `system.mcp` | System | MCP server configuration |
| `system.agent` | System | Agent definition |
| `system.environment` | System | Environment variables |
| `system.focus` | System | Channel templates |
| `system.playbook` | System | Automation scripts |

### Artifact Status (8 states)

| Status | Usage |
|--------|-------|
| `draft` | Initial creation, not ready |
| `active` | Current, in use |
| `archived` | Soft deleted |
| `pending` | Task: waiting to start |
| `in_progress` | Task: being worked on |
| `done` | Task: completed |
| `blocked` | Task: waiting on dependency |
| `published` | Content: released/public |

---

## Artifact Data Model

### Core Fields

```typescript
interface StoredArtifact {
  // Identity
  id: string;
  spaceId: string;
  channelId: string;
  slug: string;              // URL-safe identifier
  path: string;              // Hierarchical: "folder/subfolder/artifact"

  // Content
  type: ArtifactType;
  title: string;
  tldr?: string;             // Brief summary
  content?: string;          // Main content (markdown, code, etc.)
  props?: object;            // Type-specific properties

  // Metadata
  status: ArtifactStatus;
  assignees: string[];       // User/agent callsigns
  labels: string[];          // Tags
  refs: string[];            // Cross-references to other artifacts

  // Versioning
  version: number;           // Auto-incrementing
  versionName?: string;      // Named checkpoint
  versionMessage?: string;
  versionCreatedBy?: string;
  versionCreatedAt?: Date;

  // Timestamps
  createdAt: Date;
  createdBy: string;
  updatedAt: Date;
  updatedBy: string;
}
```

### Hierarchical Organization

Artifacts form a tree via `path`:

```
project-docs/                    (folder)
├── architecture/                (folder)
│   ├── adr-001-database.md     (decision)
│   └── diagrams/               (folder)
│       └── system.png          (asset)
├── tasks/                       (folder)
│   ├── task-implement-auth     (task: in_progress)
│   └── task-add-logging        (task: pending)
└── README.md                    (doc)
```

---

## CRUD Operations

### Create

```http
POST /channels/:channelId/artifacts
Content-Type: application/json

{
  "slug": "my-task",
  "type": "task",
  "title": "Implement authentication",
  "content": "## Requirements\n...",
  "status": "pending",
  "assignees": ["builder"],
  "replace": false           // Optional: overwrite existing
}
```

### Read

```http
GET /channels/:channelId/artifacts/:slug
GET /channels/:channelId/artifacts/:slug?version=v1.0
GET /channels/:channelId/artifacts?type=task&status=in_progress
```

**Query Parameters**:
- `type` - Filter by artifact type
- `status` - Filter by status
- `assignee` - Filter by assignee
- `search` - Full-text search
- `path` - Glob pattern for tree view

### Update (CAS - Compare-And-Swap)

```http
PATCH /channels/:channelId/artifacts/:slug
Content-Type: application/json

{
  "version": 5,              // Must match current version
  "status": "in_progress",
  "assignees": ["builder", "reviewer"]
}
```

Returns `409 Conflict` if version mismatch (optimistic locking).

### Surgical Edit

```http
POST /channels/:channelId/artifacts/:slug/edit
Content-Type: application/json

{
  "search": "old text",
  "replace": "new text"
}
```

String replacement within content without full rewrite.

### Delete (Archive)

```http
DELETE /channels/:channelId/artifacts/:slug
DELETE /channels/:channelId/artifacts/:slug?recursive=true
```

Soft delete - transitions to `archived` status.

---

## Version Control

### Create Checkpoint

```http
POST /channels/:channelId/artifacts/:slug/versions
Content-Type: application/json

{
  "version": "v1.0",
  "message": "Initial release",
  "sender": "human"
}
```

### List Versions

```http
GET /channels/:channelId/artifacts/:slug/versions

Response:
[
  {"name": "v1.0", "message": "Initial release", "createdBy": "human", "createdAt": "..."},
  {"name": "v1.1", "message": "Bug fixes", "createdBy": "builder", "createdAt": "..."}
]
```

### Diff Versions

```http
GET /channels/:channelId/artifacts/:slug/diff?from=v1.0&to=v1.1
```

---

## Task Workflow

Tasks are artifacts with status-based lifecycle:

```
┌─────────┐
│ pending │ (created, not started)
└────┬────┘
     │ start
     ▼
┌─────────────┐
│ in_progress │ (being worked)
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌──────┐  ┌─────────┐
│ done │  │ blocked │
└──────┘  └────┬────┘
               │ unblock
               ▼
         ┌─────────────┐
         │ in_progress │
         └─────────────┘
```

### Task Display

In tree views, task status is shown in parentheses:
- `task-auth (pending)`
- `task-auth (in_progress)`
- `task-auth (done)`

---

## Cross-References

Artifacts can reference each other via the `refs` field:

```typescript
{
  "slug": "task-implement-auth",
  "refs": [
    "adr-001-database",       // Related decision
    "task-setup-db"           // Dependency
  ]
}
```

This enables:
- Dependency tracking
- Related artifact discovery
- Impact analysis

---

## Real-Time Synchronization

### WebSocket Broadcast

All mutations broadcast to connected clients:

```typescript
connectionManager.broadcast(channelId, {
  type: 'artifact_updated',
  artifact: updatedArtifact
});
```

### Conflict Resolution

CAS (Compare-And-Swap) prevents lost updates:
1. Client reads artifact (version N)
2. Client sends PATCH with `version: N`
3. Server checks current version
4. If match → apply update, increment version
5. If mismatch → return 409 with current state

---

## Mapping to Agentive Starter Kit

### Direct Mappings

| Miriad | Agentive Starter Kit |
|--------|---------------------|
| Channel | Project scope / feature branch |
| Artifact (doc) | Markdown files in `.kit/context/` |
| Artifact (task) | Task files in `.kit/delegation/tasks/` |
| Artifact (decision) | ADRs in `docs/decisions/` |
| Artifact (folder) | Directories |
| Roster | `agent-handoffs.json` |

### Status Mapping

| Miriad Status | Our Status | Folder |
|---------------|------------|--------|
| `draft` | (not used) | N/A |
| `pending` | `Todo` | `2-todo/` |
| `in_progress` | `In Progress` | `3-in-progress/` |
| `done` | `Done` | `5-done/` |
| `blocked` | `Blocked` | `7-blocked/` |
| `archived` | (archived) | `8-archive/` |

### What We Can Adopt

1. **Structured Task Metadata**
   ```yaml
   # In task frontmatter
   type: task
   status: in_progress
   assignees: [feature-developer]
   refs: [KIT-ADR-0021, ASK-0030]
   labels: [agent-communication, priority-high]
   ```

2. **Version Checkpoints**
   - Git commits already provide versioning
   - Could add explicit "checkpoint" commits with tags

3. **Cross-References**
   - Add `refs:` field to task files
   - Parse for dependency tracking

4. **Surgical Edits**
   - Already have via Edit tool
   - Could formalize as API pattern

### What Needs Adaptation

| Miriad Feature | Our Adaptation |
|----------------|----------------|
| Real-time broadcast | File watcher + terminal notifications |
| WebSocket sync | Git pull/push + file polling |
| PostgreSQL storage | Filesystem + git |
| CAS locking | Git merge conflicts |
| API endpoints | CLI commands / file operations |

---

## Proposed Enhancements

### Enhanced Task Format

```markdown
---
id: ASK-0042
type: task
title: Implement agent-to-agent messaging
status: in_progress
assignees:
  - feature-developer
refs:
  - KIT-ADR-0021
  - ASK-0030
labels:
  - agent-communication
  - priority-high
created: 2026-02-05
updated: 2026-02-05
---

## Summary
...
```

### Channel-Like Organization

```
.kit/context/
├── channels/
│   ├── main/                  # Default channel
│   │   ├── roster.json        # Active agents
│   │   └── messages.ndjson    # Message log (from Phase 2)
│   └── feature-auth/          # Feature-specific
│       ├── roster.json
│       └── messages.ndjson
└── artifacts/
    ├── decisions/             # ADRs
    ├── docs/                  # Documentation
    └── tasks/                 # Task references
```

### Dependency Tracking

```bash
# CLI command to show task dependencies
./scripts/project deps ASK-0042

ASK-0042: Implement agent-to-agent messaging
├── depends-on:
│   └── ASK-0030: Set up message infrastructure (done)
├── blocks:
│   └── ASK-0045: Add multi-agent collaboration (pending)
└── related:
    └── KIT-ADR-0021: Real-time agent communication
```

---

## Key Takeaways

1. **Artifact Type System**: Their 12 types cover all collaboration needs. We use a subset (doc, task, decision, folder) effectively.

2. **Status Workflow**: Their 8 statuses are more granular than ours. Consider adding `blocked` and `published`.

3. **Versioning**: Git provides equivalent functionality. Named tags could map to their version checkpoints.

4. **Cross-References**: Adding `refs` field enables dependency and impact tracking.

5. **Real-Time Updates**: File watchers can approximate their WebSocket broadcasts for CLI.

---

**Phase 3 Status**: ✅ Complete
**Recommendation**: Adopt artifact type taxonomy and status workflow; implement cross-references; use file watchers for "real-time" CLI updates.
