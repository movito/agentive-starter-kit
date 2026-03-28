# ASK-0011: Task Status ↔ Linear Alignment ADR

**Status**: Done
**Priority**: medium
**Assigned To**: planner
**Estimated Effort**: 2-3 hours
**Created**: 2025-11-28

## Related Tasks

**Parent Task**: None (ADR Migration - Tier 2: Agent Coordination)
**Depends On**: ASK-0006 (Adversarial Workflow - for context)
**Blocks**: None
**Related**: ASK-0012 (Real-Time Task Monitoring), ADR-0003 (Linear Sync vs MCP)

## Overview

Adapt and document the Task Status ↔ Linear Alignment pattern from thematic-cuts (TC ADR-0038) for the agentive-starter-kit. This ADR documents the bidirectional relationship between local task files and Linear issues.

**Source**: `thematic-cuts/docs/decisions/adr/ADR-0038-task-status-linear-alignment.md`

**Why Valuable**: Establishes the authoritative pattern for how task status flows between git-tracked markdown files and Linear. Complements our existing ADR-0003 (Linear Sync vs MCP) with implementation details.

## Key Concepts to Document

### Status Flow

```
Task File (Source of Truth)
    ↓ sync
Linear Issue (Team Visibility)
    ↓ (future: reverse sync)
Task File Updated
```

### Status Priority Resolution

```
Priority 1: Status field in file (if Linear-native)
    ↓
Priority 2: Folder location (1-backlog/ through 7-blocked/)
    ↓
Priority 3: Default to "Backlog"
```

### Linear-Native Status Values

| Value | Folder | Description |
|-------|--------|-------------|
| Backlog | 1-backlog/ | Planned, not started |
| Todo | 2-todo/ | Ready to work |
| In Progress | 3-in-progress/ | Currently active |
| In Review | 4-in-review/ | Awaiting review |
| Done | 5-done/ | Completed |
| Canceled | 6-canceled/ | Abandoned |
| Blocked | 7-blocked/ | Waiting on dependency |

### Legacy Status Migration

```
draft/planning/ready → Backlog
in_progress         → In Progress
review/testing      → In Review
completed           → Done
```

## Requirements

### Functional Requirements
1. Document the status alignment pattern as an ADR
2. Explain priority resolution (field > folder > default)
3. Document legacy status migration
4. Reference existing sync infrastructure

### Non-Functional Requirements
- ADR follows project template
- Complements ADR-0003 (decision) with ADR-0009 (implementation pattern)
- Clear mapping tables

## Acceptance Criteria

### Must Have
- [ ] ADR-0009 created following project template
- [ ] Documents 3-level status priority resolution
- [ ] Includes complete status mapping table
- [ ] Explains legacy migration behavior
- [ ] References `docs/LINEAR-SYNC-BEHAVIOR.md`

### Should Have
- [ ] Diagram of status flow
- [ ] Edge case handling
- [ ] Future bidirectional sync considerations

## Implementation Plan

1. **Read source ADR** from thematic-cuts
2. **Review existing docs** (`docs/LINEAR-SYNC-BEHAVIOR.md`, ADR-0003)
3. **Adapt for starter-kit** - Ensure consistency
4. **Create ADR-0009** in `docs/decisions/adr/`

## Success Metrics

### Quantitative
- ADR created and follows template
- All acceptance criteria met

### Qualitative
- Clear status mapping for agents
- Consistent with existing documentation

## Time Estimate

| Phase | Time |
|-------|------|
| Read source ADR | 30 min |
| Review existing docs | 30 min |
| Adapt and write | 1-1.5 hours |
| Review and finalize | 30 min |
| **Total** | **2-3 hours** |

## References

- Source: `thematic-cuts/docs/decisions/adr/ADR-0038-task-status-linear-alignment.md`
- Existing: `docs/LINEAR-SYNC-BEHAVIOR.md`
- Related: `docs/decisions/adr/ADR-0003-linear-sync-vs-mcp.md`
- Sync script: `scripts/sync_tasks_to_linear.py`

## Notes

- This ADR complements ADR-0003 which covers the "why" (custom sync vs MCP)
- This ADR covers the "how" (status mapping implementation)
- Much of the content may already exist in LINEAR-SYNC-BEHAVIOR.md

---

**Template Version**: 1.0.0
**Created**: 2025-11-28
