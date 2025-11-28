# ASK-0012: Real-Time Task Monitoring ADR

**Status**: Done
**Priority**: low
**Assigned To**: planner
**Estimated Effort**: 2-3 hours
**Created**: 2025-11-28

## Related Tasks

**Parent Task**: None (ADR Migration - Tier 2: Agent Coordination)
**Depends On**: ASK-0011 (Task Status Alignment)
**Blocks**: None
**Related**: ASK-0014 (Workflow Observation)

## Overview

Adapt and document the Real-Time Task Monitoring pattern from thematic-cuts (TC ADR-0039) for the agentive-starter-kit. This ADR documents live task dashboards with file watching and optional WebSocket updates.

**Source**: `thematic-cuts/docs/decisions/adr/ADR-0039-real-time-task-monitoring.md`

**Why Valuable**: Enables visibility into multi-agent task execution. Users can see task status changes as they happen, improving coordination and debugging.

## Key Concepts to Document

### Monitoring Architecture

```
File System Watch (task folders)
    ↓
Task Status Parser
    ↓
Event Emitter
    ↓
Dashboard / WebSocket / CLI
```

### Monitoring Modes

1. **CLI Mode** - Terminal-based status display
2. **Daemon Mode** - Background file watcher
3. **Dashboard Mode** - Web-based UI (future)

### Task Monitor Daemon

```bash
# Start monitoring
./project daemon start

# Check status
./project daemon status

# View logs
./project daemon logs

# Stop monitoring
./project daemon stop
```

### Events Tracked

| Event | Trigger | Data |
|-------|---------|------|
| task_created | New file in task folder | Task ID, title, status |
| task_moved | File moved between folders | Task ID, old status, new status |
| task_updated | File content changed | Task ID, changed fields |
| task_deleted | File removed | Task ID |

## Requirements

### Functional Requirements
1. Document the monitoring architecture as an ADR
2. Explain daemon mode operation
3. Document event types and data
4. Show CLI usage patterns

### Non-Functional Requirements
- ADR follows project template
- Practical examples included
- Performance considerations documented

## Acceptance Criteria

### Must Have
- [ ] ADR-0010 created following project template
- [ ] Documents file watching approach
- [ ] Explains daemon start/stop commands
- [ ] Lists event types and payloads
- [ ] References existing daemon infrastructure

### Should Have
- [ ] Performance considerations (debouncing)
- [ ] Error handling for file system events
- [ ] Future WebSocket/dashboard considerations

### Nice to Have
- [ ] Integration with Linear sync
- [ ] Notification patterns

## Implementation Plan

1. **Read source ADR** from thematic-cuts
2. **Audit existing daemon** in starter-kit (if any)
3. **Adapt for starter-kit** - Focus on core monitoring
4. **Create ADR-0010** in `docs/decisions/adr/`

## Success Metrics

### Quantitative
- ADR created and follows template
- All acceptance criteria met

### Qualitative
- Clear daemon operation guide
- Event-driven pattern documented

## Time Estimate

| Phase | Time |
|-------|------|
| Read source ADR | 30 min |
| Audit existing infrastructure | 30 min |
| Adapt and write | 1-1.5 hours |
| Review and finalize | 30 min |
| **Total** | **2-3 hours** |

## References

- Source: `thematic-cuts/docs/decisions/adr/ADR-0039-real-time-task-monitoring.md`
- Daemon docs: `docs/LINEAR-SYNC-BEHAVIOR.md` (Task Monitor section)
- watchdog: https://pypi.org/project/watchdog/

## Notes

- Starter-kit may have basic daemon infrastructure
- This ADR documents the pattern for future implementation
- WebSocket/dashboard is future scope

---

**Template Version**: 1.0.0
**Created**: 2025-11-28
