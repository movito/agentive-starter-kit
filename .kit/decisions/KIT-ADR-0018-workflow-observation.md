# KIT-ADR-0018: Workflow Observation Architecture

**Status**: Accepted

**Date**: 2025-11-29

**Deciders**: planner, User

## Context

### Problem Statement

Multi-agent systems have complex workflows with handoffs, parallel tasks, and state changes. Understanding what's happening requires visibility into agent actions, task progress, and system health. Without structured observation:
- Debugging agent behavior is difficult
- Performance bottlenecks are hidden
- Handoff failures go unnoticed
- System health is opaque

### Forces at Play

**Technical Requirements:**
- Capture events across multiple agents
- Store events for later analysis
- Enable real-time monitoring dashboards
- Support filtering and querying
- Integrate with existing logging (KIT-ADR-0009)

**Constraints:**
- Agents run in separate processes/sessions
- Events must be lightweight (low overhead)
- Storage should be append-only (immutable log)
- Multiple observers may consume events

**Assumptions:**
- Projects may have multiple concurrent agents
- Event volume is moderate (not high-frequency trading)
- Observers are decoupled from emitters
- Events are structured JSON

## Decision

We will adopt an **event-driven workflow observation architecture** with structured events, append-only storage, and pluggable observers.

### Core Principles

1. **Event sourcing**: All state changes captured as events
2. **Structured format**: Events follow a consistent schema
3. **Append-only log**: Events are immutable once written
4. **Pluggable observers**: Dashboard, logs, analytics can subscribe

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Activities                          │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                 │
│  │ Planner │    │Developer│    │ Tester  │                 │
│  └────┬────┘    └────┬────┘    └────┬────┘                 │
│       │              │              │                       │
│       ▼              ▼              ▼                       │
│  ┌────────────────────────────────────────┐                 │
│  │           Event Emitters               │                 │
│  │  emit_task_event(), emit_agent_event() │                 │
│  └────────────────────┬───────────────────┘                 │
│                       │                                      │
│                       ▼                                      │
│  ┌────────────────────────────────────────┐                 │
│  │           Event Log (append-only)      │                 │
│  │     .agent-context/events/YYYY-MM-DD.jsonl               │
│  └────────────────────┬───────────────────┘                 │
│                       │                                      │
│          ┌───────────┼───────────┐                          │
│          ▼           ▼           ▼                          │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐                 │
│  │ Dashboard │ │ Log Sink  │ │ Analytics │                 │
│  │ (Realtime)│ │(Structured)│ │ (Metrics) │                 │
│  └───────────┘ └───────────┘ └───────────┘                 │
│                   Observers                                  │
└─────────────────────────────────────────────────────────────┘
```

### Event Schema

**Base Event Structure**

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
import uuid

@dataclass
class WorkflowEvent:
    """Base event structure for workflow observation."""

    # Required fields
    event_type: str                    # e.g., "task.started", "agent.handoff"
    timestamp: datetime                # When event occurred
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Context fields
    agent: Optional[str] = None        # Which agent emitted event
    task_id: Optional[str] = None      # Related task ID
    session_id: Optional[str] = None   # Session/conversation ID

    # Event-specific data
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "agent": self.agent,
            "task_id": self.task_id,
            "session_id": self.session_id,
            "metadata": self.metadata
        }
```

### Event Types

**Category: Task Lifecycle**

| Event Type | When Emitted | Key Metadata |
|------------|--------------|--------------|
| `task.created` | New task file created | priority, estimated_effort |
| `task.started` | Agent begins task | agent, start_time |
| `task.completed` | Task finished successfully | duration, outcome |
| `task.failed` | Task failed | error_type, error_message |
| `task.blocked` | Task cannot proceed | blocker_reason, blocker_task |
| `task.status_changed` | Status field updated | old_status, new_status |

**Category: Agent Activity**

| Event Type | When Emitted | Key Metadata |
|------------|--------------|--------------|
| `agent.activated` | Agent session started | agent_type, tools_available |
| `agent.handoff` | Work transferred | from_agent, to_agent, context |
| `agent.completed` | Agent finished session | tasks_completed, duration |
| `agent.error` | Agent encountered error | error_type, recoverable |

**Category: Tool Usage**

| Event Type | When Emitted | Key Metadata |
|------------|--------------|--------------|
| `tool.called` | Tool invocation started | tool_name, parameters |
| `tool.succeeded` | Tool returned successfully | duration, result_size |
| `tool.failed` | Tool returned error | error_type, error_message |

**Category: System Health**

| Event Type | When Emitted | Key Metadata |
|------------|--------------|--------------|
| `system.started` | System/service started | version, config |
| `system.health_check` | Periodic health check | status, metrics |
| `system.error` | System-level error | error_type, severity |
| `system.shutdown` | Graceful shutdown | reason, uptime |

### Implementation Details

**Event Emitter**

```python
# scripts/workflow_events.py
import json
from pathlib import Path
from datetime import datetime, date
from typing import Optional, Any

class WorkflowEventEmitter:
    """Emit events to the workflow observation log."""

    def __init__(self, events_dir: str = ".agent-context/events"):
        self.events_dir = Path(events_dir)
        self.events_dir.mkdir(parents=True, exist_ok=True)
        self._current_session: Optional[str] = None
        self._current_agent: Optional[str] = None

    def set_context(self, agent: str, session_id: str) -> None:
        """Set context for all subsequent events."""
        self._current_agent = agent
        self._current_session = session_id

    def emit(
        self,
        event_type: str,
        task_id: Optional[str] = None,
        **metadata
    ) -> None:
        """
        Emit a workflow event.

        Args:
            event_type: Type of event (e.g., "task.started")
            task_id: Related task ID (optional)
            **metadata: Additional event-specific data
        """
        event = WorkflowEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            agent=self._current_agent,
            task_id=task_id,
            session_id=self._current_session,
            metadata=metadata
        )

        self._write_event(event)

    def _write_event(self, event: WorkflowEvent) -> None:
        """Append event to today's log file."""
        log_file = self.events_dir / f"{date.today().isoformat()}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(event.to_json()) + "\n")


# Convenience functions
_emitter = WorkflowEventEmitter()

def emit_task_event(event_type: str, task_id: str, **metadata) -> None:
    """Emit a task-related event."""
    _emitter.emit(event_type, task_id=task_id, **metadata)

def emit_agent_event(event_type: str, **metadata) -> None:
    """Emit an agent-related event."""
    _emitter.emit(event_type, **metadata)
```

**Event Reader**

```python
# scripts/event_reader.py
import json
from pathlib import Path
from datetime import date, timedelta
from typing import Iterator, Optional

def read_events(
    days_back: int = 7,
    event_types: Optional[list[str]] = None,
    agent: Optional[str] = None,
    task_id: Optional[str] = None,
    events_dir: str = ".agent-context/events"
) -> Iterator[dict]:
    """
    Read events from the log with optional filtering.

    Args:
        days_back: How many days of events to read
        event_types: Filter by event types (e.g., ["task.started", "task.completed"])
        agent: Filter by agent name
        task_id: Filter by task ID

    Yields:
        Matching events as dictionaries
    """
    events_path = Path(events_dir)
    today = date.today()

    for i in range(days_back):
        log_date = today - timedelta(days=i)
        log_file = events_path / f"{log_date.isoformat()}.jsonl"

        if not log_file.exists():
            continue

        with open(log_file) as f:
            for line in f:
                event = json.loads(line)

                # Apply filters
                if event_types and event["event_type"] not in event_types:
                    continue
                if agent and event.get("agent") != agent:
                    continue
                if task_id and event.get("task_id") != task_id:
                    continue

                yield event
```

**Integration with Logging**

```python
# Integration with KIT-ADR-0009 logging
import logging
from scripts.workflow_events import emit_task_event

logger = logging.getLogger("agentive.sync")

def sync_task_to_linear(task: Task) -> None:
    """Sync task with event emission."""
    # Emit start event
    emit_task_event("task.sync_started", task.id, target="linear")

    try:
        linear_client.sync(task)

        # Emit success event
        emit_task_event("task.sync_completed", task.id, target="linear")
        logger.info(f"Synced task {task.id} to Linear")

    except LinearError as e:
        # Emit failure event
        emit_task_event(
            "task.sync_failed",
            task.id,
            target="linear",
            error_type=type(e).__name__,
            error_message=str(e)
        )
        logger.error(f"Failed to sync task {task.id}: {e}")
        raise
```

### Observer Patterns

**Pattern 1: Real-time Dashboard**

```python
# observers/dashboard.py
import json
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class EventFileHandler(FileSystemEventHandler):
    """Watch event files for new events."""

    def on_modified(self, event):
        if event.src_path.endswith('.jsonl'):
            # Read new events and update dashboard
            self._process_new_events(event.src_path)

    def _process_new_events(self, path: str) -> None:
        """Process newly added events."""
        # Implementation: read last N lines, update UI
        pass


def start_dashboard(events_dir: str = ".agent-context/events"):
    """Start real-time event dashboard."""
    observer = Observer()
    observer.schedule(EventFileHandler(), events_dir)
    observer.start()
```

**Pattern 2: Metrics Aggregation**

```python
# observers/metrics.py
from collections import Counter
from scripts.event_reader import read_events

def compute_task_metrics(days: int = 7) -> dict:
    """Compute task-related metrics from events."""
    events = list(read_events(
        days_back=days,
        event_types=["task.started", "task.completed", "task.failed"]
    ))

    started = [e for e in events if e["event_type"] == "task.started"]
    completed = [e for e in events if e["event_type"] == "task.completed"]
    failed = [e for e in events if e["event_type"] == "task.failed"]

    # Compute durations for completed tasks
    durations = []
    for c in completed:
        if "duration" in c.get("metadata", {}):
            durations.append(c["metadata"]["duration"])

    return {
        "tasks_started": len(started),
        "tasks_completed": len(completed),
        "tasks_failed": len(failed),
        "completion_rate": len(completed) / max(len(started), 1),
        "avg_duration_minutes": sum(durations) / max(len(durations), 1),
        "by_agent": Counter(e.get("agent") for e in events)
    }
```

**Pattern 3: Alert System**

```python
# observers/alerts.py
from typing import Callable
from scripts.event_reader import read_events

def check_failure_rate(
    threshold: float = 0.2,
    window_hours: int = 24,
    on_alert: Callable[[str], None] = print
) -> None:
    """Alert if failure rate exceeds threshold."""
    events = list(read_events(
        days_back=1,
        event_types=["task.completed", "task.failed"]
    ))

    if not events:
        return

    failed = sum(1 for e in events if e["event_type"] == "task.failed")
    rate = failed / len(events)

    if rate > threshold:
        on_alert(f"ALERT: Task failure rate {rate:.1%} exceeds {threshold:.1%}")
```

### Storage Considerations

**File Format: JSONL**

- One JSON object per line
- Easy to append (no JSON array closing bracket issues)
- Easy to stream and process
- Human-readable

**Rotation Strategy**

```python
# Daily rotation is automatic (date in filename)
.agent-context/events/
├── 2025-11-27.jsonl
├── 2025-11-28.jsonl
└── 2025-11-29.jsonl

# Archive old events (optional script)
def archive_old_events(days_to_keep: int = 30):
    """Move old event files to archive."""
    events_dir = Path(".agent-context/events")
    archive_dir = Path(".agent-context/events/archive")

    cutoff = date.today() - timedelta(days=days_to_keep)

    for f in events_dir.glob("*.jsonl"):
        file_date = date.fromisoformat(f.stem)
        if file_date < cutoff:
            f.rename(archive_dir / f.name)
```

**Size Estimation**

| Volume | Events/Day | File Size | 30-Day Total |
|--------|------------|-----------|--------------|
| Low | ~100 | ~50 KB | ~1.5 MB |
| Medium | ~1,000 | ~500 KB | ~15 MB |
| High | ~10,000 | ~5 MB | ~150 MB |

## Consequences

### Positive

- ✅ **Full visibility**: All workflow state changes captured
- ✅ **Debugging**: Replay events to understand failures
- ✅ **Metrics**: Compute KPIs from event stream
- ✅ **Decoupled**: Emitters and observers are independent
- ✅ **Lightweight**: Append-only, no database needed

### Negative

- ⚠️ **Storage growth**: Events accumulate over time
- ⚠️ **Query limits**: JSONL not optimized for complex queries
- ⚠️ **Discipline**: Developers must emit events consistently

### Neutral

- 📊 **Schema evolution**: New event types easy to add
- 📊 **No real-time guarantee**: File-based, not streaming

## Alternatives Considered

### Alternative 1: Database Storage

**Description**: Store events in SQLite or PostgreSQL.

**Rejected because**:
- ❌ Adds database dependency
- ❌ More complex setup
- ⚠️ Could be added later for querying

### Alternative 2: OpenTelemetry

**Description**: Use OpenTelemetry for tracing and metrics.

**Deferred because**:
- ✅ Industry standard
- ✅ Rich ecosystem
- ⚠️ Higher complexity for small projects
- 📊 Can migrate to OTel later

### Alternative 3: No Event System

**Description**: Rely solely on logging.

**Rejected because**:
- ❌ Logs are unstructured
- ❌ Hard to query and aggregate
- ❌ No event correlation

## Related Decisions

- KIT-ADR-0009: Logging & Observability (complementary to events)
- KIT-ADR-0013: Real-Time Task Monitoring (consumes events)

## References

- Event Sourcing: https://martinfowler.com/eaaDev/EventSourcing.html
- OpenTelemetry: https://opentelemetry.io/
- JSONL Format: https://jsonlines.org/

## Revision History

- 2025-11-29: Initial decision (Accepted)
  - Established event-driven observation architecture
  - Defined event schema and types
  - Documented observer patterns

---

**Template Version**: 1.1.0
**Last Updated**: 2025-11-29
**Project**: agentive-starter-kit
