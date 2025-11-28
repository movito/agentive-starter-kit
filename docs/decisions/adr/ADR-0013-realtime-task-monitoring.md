# ADR-0013: Real-Time Task Monitoring

**Status**: Accepted

**Date**: 2025-11-28

**Deciders**: planner, User

## Context

### Problem Statement

Task status changes currently only sync to Linear on git push (via CI). During active development sessions with multiple agents, users lack visibility into:
- Which tasks are being worked on
- When tasks change status (move between folders)
- Real-time progress of multi-agent workflows

We need a monitoring pattern that provides immediate visibility without requiring manual checks.

### Forces at Play

**Technical Requirements:**
- Watch file system for task folder changes
- Parse task metadata on change
- Emit events for status transitions
- Support multiple output modes (CLI, daemon, future dashboard)

**Constraints:**
- Must work without external services
- Should not interfere with sync operations
- Must handle rapid file changes (debouncing)
- Should be optional (not required for basic operation)

**Assumptions:**
- Tasks are organized in numbered folders
- File changes are the source of truth
- Users want immediate feedback during sessions

## Decision

We will adopt an **event-driven file watching architecture** with daemon mode for background monitoring and optional CLI/dashboard outputs.

### Core Principles

1. **File system as event source**: Watch task folders for changes
2. **Event-driven**: Emit typed events for all task transitions
3. **Daemon-capable**: Run as background process
4. **Debounced updates**: Coalesce rapid changes

### Implementation Details

**Monitoring Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│                   File System Events                     │
│     (create, modify, move, delete in task folders)      │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    File Watcher                          │
│              (watchdog library)                          │
│    - Watches: delegation/tasks/*/                       │
│    - Debounce: 500ms                                    │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Task Parser                             │
│    - Extract: task_id, title, status, priority          │
│    - Detect: status changes, folder moves               │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Event Emitter                           │
│    Events: task_created, task_moved, task_updated       │
└─────────────────────────┬───────────────────────────────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
      ┌──────────┐  ┌──────────┐  ┌──────────┐
      │   CLI    │  │  Linear  │  │ Dashboard│
      │  Output  │  │   Sync   │  │ (future) │
      └──────────┘  └──────────┘  └──────────┘
```

**Event Types:**

| Event | Trigger | Payload |
|-------|---------|---------|
| `task_created` | New file in task folder | `{task_id, title, status, folder, timestamp}` |
| `task_moved` | File moved between folders | `{task_id, old_folder, new_folder, old_status, new_status, timestamp}` |
| `task_updated` | File content changed | `{task_id, changed_fields, timestamp}` |
| `task_deleted` | File removed | `{task_id, folder, timestamp}` |

**Daemon Commands:**

```bash
# Start the monitoring daemon
./project daemon start

# Check if daemon is running
./project daemon status

# View daemon logs
./project daemon logs

# Stop the daemon
./project daemon stop

# Run in foreground (for debugging)
./project daemon run
```

**Implementation Pattern (Python):**

```python
# scripts/task_monitor.py
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Callable
import json

@dataclass
class TaskEvent:
    event_type: str  # task_created, task_moved, task_updated, task_deleted
    task_id: str
    timestamp: datetime
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    changed_fields: Optional[list] = None

class TaskEventHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[TaskEvent], None], debounce_ms: int = 500):
        self.callback = callback
        self.debounce_ms = debounce_ms
        self._pending = {}

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return
        self._emit_debounced('task_created', event.src_path)

    def on_moved(self, event):
        if event.is_directory or not event.dest_path.endswith('.md'):
            return
        self._emit_debounced('task_moved', event.dest_path, event.src_path)

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return
        self._emit_debounced('task_updated', event.src_path)

    def on_deleted(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return
        self._emit_debounced('task_deleted', event.src_path)

    def _emit_debounced(self, event_type: str, path: str, old_path: str = None):
        # Debounce implementation
        # ... coalesce rapid changes
        pass

def start_monitor(task_dir: Path, callback: Callable[[TaskEvent], None]):
    """Start file system monitoring."""
    event_handler = TaskEventHandler(callback)
    observer = Observer()
    observer.schedule(event_handler, str(task_dir), recursive=True)
    observer.start()
    return observer
```

**CLI Output Mode:**

```python
def cli_output(event: TaskEvent):
    """Print event to console."""
    timestamp = event.timestamp.strftime("%H:%M:%S")

    if event.event_type == 'task_created':
        print(f"[{timestamp}] ✨ Created: {event.task_id} ({event.new_status})")
    elif event.event_type == 'task_moved':
        print(f"[{timestamp}] 📦 Moved: {event.task_id}: {event.old_status} → {event.new_status}")
    elif event.event_type == 'task_updated':
        print(f"[{timestamp}] 📝 Updated: {event.task_id}")
    elif event.event_type == 'task_deleted':
        print(f"[{timestamp}] 🗑️  Deleted: {event.task_id}")
```

**Daemon Mode (PID file):**

```python
# scripts/daemon.py
import os
import sys
from pathlib import Path

PIDFILE = Path.home() / '.cache' / 'agentive' / 'monitor.pid'

def daemon_start():
    """Start daemon in background."""
    if PIDFILE.exists():
        print("Daemon already running")
        return

    # Fork and daemonize
    pid = os.fork()
    if pid > 0:
        # Parent - write PID and exit
        PIDFILE.parent.mkdir(parents=True, exist_ok=True)
        PIDFILE.write_text(str(pid))
        print(f"✅ Daemon started (PID: {pid})")
        return

    # Child - run monitor
    run_monitor()

def daemon_stop():
    """Stop running daemon."""
    if not PIDFILE.exists():
        print("No daemon running")
        return

    pid = int(PIDFILE.read_text())
    os.kill(pid, signal.SIGTERM)
    PIDFILE.unlink()
    print("✅ Daemon stopped")
```

**Performance Considerations:**

| Concern | Mitigation |
|---------|------------|
| Rapid file changes | 500ms debounce window |
| Large task folders | Watch specific subfolders only |
| Memory usage | Process events, don't cache all files |
| CPU on idle | Watchdog uses inotify (Linux) / FSEvents (macOS) |

**Linear Sync Integration:**

When monitor detects `task_moved`:
1. Update status field in file (if not matching folder)
2. Optionally trigger immediate Linear sync
3. Log the transition for audit

```python
def on_task_moved(event: TaskEvent):
    """Handle task folder move."""
    # Update status field to match new folder
    update_task_status(event.task_id, event.new_status)

    # Optionally sync to Linear immediately
    if IMMEDIATE_SYNC:
        sync_task_to_linear(event.task_id)
```

## Consequences

### Positive

- ✅ **Real-time visibility**: See changes as they happen
- ✅ **Background operation**: Daemon mode doesn't block terminal
- ✅ **Event-driven**: Clean architecture for future extensions
- ✅ **Linear integration**: Can trigger immediate sync

### Negative

- ⚠️ **Resource usage**: Background process consumes resources
- ⚠️ **Platform differences**: File watching varies by OS
- ⚠️ **Complexity**: Daemon management adds operational overhead

### Neutral

- 📊 **Optional feature**: Not required for basic workflow
- 📊 **Future dashboard**: WebSocket layer can be added later

## Alternatives Considered

### Alternative 1: Polling-Based Monitoring

**Description**: Periodically scan task folders instead of file watching

**Rejected because**:
- ❌ Higher resource usage (constant scanning)
- ❌ Latency (depends on poll interval)
- ❌ Less efficient than OS-native events

### Alternative 2: Git Hook-Based

**Description**: Trigger monitoring on git operations only

**Rejected because**:
- ❌ Misses uncommitted changes
- ❌ No real-time feedback during editing
- ❌ Doesn't track folder moves before commit

### Alternative 3: Editor Plugin

**Description**: Monitor via VS Code / IDE extension

**Rejected because**:
- ❌ Editor-specific implementation
- ❌ Doesn't work with CLI-based workflows
- ❌ Requires plugin installation

## Implementation Status

**Current State**: Pattern documented, not implemented

**When to Implement**: When real-time monitoring becomes a priority

**First Steps**:
1. Add `watchdog` to dependencies
2. Create `scripts/task_monitor.py`
3. Add daemon commands to `./project` CLI
4. Create `scripts/daemon.py` for background mode

## Related Decisions

- ADR-0003: Linear Sync vs MCP (sync strategy)
- ADR-0012: Task Status Linear Alignment (status mapping)
- ADR-0009: Logging & Observability (event logging)

## References

- watchdog library: https://pypi.org/project/watchdog/
- python-daemon: https://pypi.org/project/python-daemon/
- FSEvents (macOS): https://developer.apple.com/documentation/coreservices/file_system_events
- inotify (Linux): https://man7.org/linux/man-pages/man7/inotify.7.html

## Revision History

- 2025-11-28: Initial decision (Accepted)
  - Documented file watching architecture
  - Defined event types and daemon commands
  - Established performance considerations

---

**Template Version**: 1.1.0
**Last Updated**: 2025-11-28
**Project**: agentive-starter-kit
