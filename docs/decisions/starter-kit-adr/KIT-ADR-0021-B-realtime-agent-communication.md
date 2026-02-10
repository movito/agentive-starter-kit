# KIT-ADR-0021-B: Real-Time Agent Communication (Revised)

**Status**: Proposed

**Date**: 2026-02-05

**Deciders**: movito, planner

**Supersedes**: KIT-ADR-0021 (original proposal)

**Research Basis**: Miriad-app architecture analysis (6 phases)

## Context

The agentive-starter-kit architecture uses file-based coordination (`agent-handoffs.json`, task folders, handoff documents) which works well for sequential, asynchronous workflows. However, agents cannot communicate directly with each other—all inter-agent communication flows through the human operator who manually relays context between terminal sessions.

### Problem Statement

Human operators are forced to act as message routers between agents, creating a bottleneck that doesn't scale and is exhausting to maintain. We need a mechanism for agents to address and communicate with each other directly while preserving human visibility and intervention capability.

```
Current Flow:
┌─────────────┐     ┌─────────┐     ┌─────────────┐
│ Agent A     │ ──► │  Human  │ ──► │ Agent B     │
│ (terminal)  │ ◄── │ (relay) │ ◄── │ (terminal)  │
└─────────────┘     └─────────┘     └─────────────┘

Desired Flow:
┌─────────────┐                     ┌─────────────┐
│ Agent A     │ ◄──────────────────►│ Agent B     │
│             │    (direct comms)   │             │
└─────────────┘                     └─────────────┘
        │                                   │
        └───────────► Human ◄───────────────┘
                   (observes/intervenes)
```

### Research Findings

Analysis of sanity-labs/miriad-app revealed proven patterns for multi-agent communication:

| Miriad Feature | Our Adaptation |
|----------------|----------------|
| Tymbal protocol (WebSocket) | File-based NDJSON variant |
| 9 message types | Adopt taxonomy directly |
| @mention routing | File-based equivalent |
| ULID ordering | Adopt directly |
| Long-running agents | Keep ephemeral model |

**Key insight**: Miriad's message taxonomy and routing patterns are transport-agnostic. We can adapt them for file-based communication while preserving our CLI-first, ephemeral-agent architecture.

### Forces at Play

**Technical Requirements:**
- Agents run as separate CLI processes (Claude Code)
- Each agent has distinct model, role, and MCP configuration
- Agents are ephemeral—they spin up, execute, and exit
- Human needs visibility into all agent conversations
- Human needs ability to intervene in any conversation

**Constraints:**
- Must work locally (no cloud dependencies required)
- Should integrate with existing file-based coordination
- Cannot modify Claude Code CLI internals
- Must preserve context-efficiency gains from current setup
- Agents remain ephemeral (no long-running processes required)

## Decision

We will implement a **file-based Tymbal variant** that adapts Miriad's proven message taxonomy and routing patterns for our ephemeral, CLI-first architecture.

### Core Principles

1. **Ephemeral-first**: Agents don't need to poll or run continuously
2. **Human as observer, not router**: Human can see all messages, intervene when needed
3. **Agents as peers**: Any agent can address any other agent via @mentions
4. **File-based persistence**: All messages stored as NDJSON for durability and Git integration
5. **Graceful degradation**: System works with or without real-time features

### Message Type Taxonomy

Adapted from Miriad's Tymbal protocol (9 types):

| Type | Direction | Purpose | Streaming |
|------|-----------|---------|-----------|
| `user` | Human → Agent | Human input | No |
| `agent` | Agent → Human/Agent | Agent responses | No |
| `tool_call` | Agent → System | Tool invocation | No |
| `tool_result` | System → Agent | Tool outcome | No |
| `thinking` | Agent internal | Reasoning (visible) | No |
| `status` | Any | Transient work indicator | No |
| `error` | Any | Error messages | No |
| `agent_complete` | Agent → System | Task completion signal | No |
| `agent_message` | Agent → Agent | Direct inter-agent communication | No |

### Message Format

```typescript
interface Message {
  id: string;           // ULID (sortable unique identifier)
  t: string;            // ISO 8601 timestamp
  type: MessageType;    // One of 9 types above
  sender: string;       // Agent callsign or "human"
  content: string;      // Message body
  addressed: string[];  // @mentioned recipients
  refs?: string[];      // Related message/artifact IDs
  metadata?: object;    // Type-specific data
}
```

**Example NDJSON line:**
```json
{"id":"01HXYZ...","t":"2026-02-05T10:30:00.000Z","type":"agent","sender":"planner","content":"@feature-developer Task ASK-0050 is ready for implementation.","addressed":["feature-developer"],"refs":["ASK-0050"]}
```

### Directory Structure

```
.agent-context/
├── channels/
│   └── main/                      # Default channel
│       ├── messages.ndjson        # Append-only message log
│       └── roster.json            # Active agents and status
├── lib/                           # Python utilities
│   ├── __init__.py
│   ├── message.py                 # Message class + serialization
│   ├── channel.py                 # Channel read/write operations
│   └── mention.py                 # @mention parsing
└── agent-handoffs.json            # Existing coordination (unchanged)
```

### Routing via @mentions

Agents address each other using `@callsign` syntax:

```
@feature-developer Please implement the auth module.
@planner @code-reviewer Ready for review.
@channel Broadcast to all agents.
```

**Visibility rules** (adapted from Miriad):
- Agents see messages where they are `@mentioned`
- Agents see messages they sent
- `@channel` broadcasts to all roster agents
- Humans see all messages

### Agent Integration

**Startup flow** (added to agent wrapper):
```
1. Read roster.json, update own status to "online"
2. Read messages.ndjson
3. Filter to messages where self is @mentioned
4. Identify unprocessed messages (by ID tracking)
5. Inject relevant messages into context
6. Process task
7. Append any outgoing messages to messages.ndjson
8. Update roster status to "offline" on exit
```

**No polling required**: Agents check inbox once at startup. For real-time response, optional file watcher mode available.

### Error Handling Strategy

**Ordering** (from Miriad research):
- Use ULID for message IDs (lexicographically sortable)
- Sort messages by ID on read, not by arrival time
- No sequence numbers or coordination needed

**Delivery guarantees**:
- Append-only logs ensure durability
- Agent reads all messages on startup (no "delivery" concept)
- Idempotent processing via message ID tracking

**Conflict resolution**:
- Concurrent appends handled by filesystem (atomic append)
- Use file locking for safety: `fcntl.flock()` or equivalent
- Git merge handles distributed sync conflicts

**Recovery**:
- Messages persist in filesystem (survive crashes)
- Agent can resume from any point using timestamp filter
- No message loss unless filesystem fails

### Resource Management

**Ephemeral mode** (default, recommended):
```
Agent starts → Checks inbox → Processes → Exits
- No background processes
- No polling
- Lowest resource usage
- Messages wait in file until next agent run
```

**File watcher mode** (optional, for faster response):
```
Agent starts → Watches inbox → Responds to new messages → Idle timeout → Exits
- Uses fswatch/inotify (no polling)
- Configurable idle timeout (default: 15 minutes)
- One process per active agent
```

### CLI Commands

```bash
# Send a message
./scripts/project message send @feature-developer "Task ready"

# Read messages for an agent
./scripts/project message inbox planner

# List all messages in channel
./scripts/project message list --channel main --since 1h

# Watch channel in real-time (human interface)
./scripts/project channel watch main

# View roster
./scripts/project channel roster main
```

### Human Interface

Terminal display for `channel watch`:

```
╭─ Channel: main ─────────────────────────────────────────────╮
│                                                              │
│ [10:30:05] @human → @planner                                │
│   Please prioritize ASK-0050                                 │
│                                                              │
│ [10:30:08] @planner 🤔                                       │
│   Analyzing task priorities...                               │
│                                                              │
│ [10:30:15] @planner → @feature-developer                    │
│   Task ASK-0050 is now top priority.                        │
│   refs: delegation/tasks/2-todo/ASK-0050.md                 │
│                                                              │
╰──────────────────────────────────────────────────────────────╯
```

## Implementation Plan

### Phase 1: Foundation (Week 1)

**Files to create:**

| File | Purpose |
|------|---------|
| `.agent-context/lib/message.py` | Message class, serialization, ULID |
| `.agent-context/lib/channel.py` | Channel read/write, roster management |
| `.agent-context/lib/mention.py` | @mention parsing |
| `.agent-context/channels/main/messages.ndjson` | Initial empty log |
| `.agent-context/channels/main/roster.json` | Initial empty roster |

**Functions:**

```python
# message.py
class Message:
    id: str
    t: str
    type: MessageType
    sender: str
    content: str
    addressed: list[str]
    refs: list[str] | None
    metadata: dict | None

def create_message(type, sender, content, addressed=None, refs=None) -> Message
def serialize(message: Message) -> str
def deserialize(line: str) -> Message
def generate_ulid() -> str

# channel.py
def append_message(channel: str, message: Message) -> None
def read_messages(channel: str, since: str = None) -> list[Message]
def filter_for_agent(messages: list[Message], agent: str) -> list[Message]
def get_roster(channel: str) -> dict
def update_roster(channel: str, agent: str, status: str) -> None

# mention.py
def parse_mentions(content: str) -> list[str]
def strip_mentions(content: str) -> str
def is_broadcast(mentions: list[str]) -> bool
```

**Tests:**
- `tests/test_message.py` - Serialization, ULID sorting
- `tests/test_channel.py` - Read/write, filtering
- `tests/test_mention.py` - @mention parsing

### Phase 2: Agent Integration (Week 2)

**Files to create/modify:**

| File | Purpose |
|------|---------|
| `scripts/agent-inbox.py` | Check inbox, format for context |
| `.claude/agents/*.md` | Add inbox check instructions |

**Agent startup injection:**
```python
# agent-inbox.py
def get_inbox_context(agent: str, channel: str = "main") -> str:
    """Returns formatted inbox messages for agent context injection."""
    messages = read_messages(channel)
    relevant = filter_for_agent(messages, agent)
    unread = get_unread(relevant, agent)
    return format_for_context(unread)
```

### Phase 3: Human Interface (Week 3)

**Files to create:**

| File | Purpose |
|------|---------|
| `scripts/channel-watch.py` | Real-time channel display |
| `scripts/project` (update) | Add message/channel commands |

### Phase 4: Enhanced Features (Week 4)

**Enhancements:**
- Cross-references via `refs` field
- Dependency tracking in tasks
- Message archival (rotate old messages)
- Multi-channel support

## Testing Requirements

### Unit Tests

```python
# test_message.py
def test_message_serialization_roundtrip()
def test_ulid_sorting_preserves_order()
def test_message_type_validation()

# test_channel.py
def test_append_message_atomic()
def test_read_messages_sorted_by_id()
def test_filter_for_agent_includes_mentions()
def test_filter_for_agent_includes_sent()
def test_filter_for_agent_includes_broadcast()

# test_mention.py
def test_parse_single_mention()
def test_parse_multiple_mentions()
def test_parse_channel_broadcast()
def test_strip_mentions()
```

### Integration Tests

```python
# test_integration.py
def test_agent_a_writes_agent_b_reads()
def test_broadcast_reaches_all_agents()
def test_message_ordering_across_writers()
def test_concurrent_appends_no_corruption()
```

### Acceptance Criteria

- [ ] Agent can send message to another agent via @mention
- [ ] Agent receives messages addressed to it on startup
- [ ] Human can observe all messages via `channel watch`
- [ ] Human can send messages to agents
- [ ] Messages persist across agent restarts
- [ ] Message ordering is consistent (ULID-based)
- [ ] No messages lost under normal operation
- [ ] System works fully offline (no network required)
- [ ] Concurrent writes don't corrupt log file

## Consequences

### Positive

- ✅ **Direct agent communication**: Agents can address each other without human relay
- ✅ **Human visibility preserved**: All messages visible via CLI
- ✅ **Ephemeral agents preserved**: No long-running processes required
- ✅ **File-based simplicity**: No server infrastructure needed
- ✅ **Git-friendly**: Message logs are text files, versionable
- ✅ **Proven patterns**: Message taxonomy from production system (Miriad)
- ✅ **Offline-capable**: Works without network connectivity

### Negative

- ⚠️ **Not real-time by default**: Messages wait for next agent run (mitigated by file watcher mode)
- ⚠️ **File I/O overhead**: Each message requires file append
- ⚠️ **Log growth**: Message files grow over time (mitigated by archival)

### Neutral

- 📊 **Agent startup changes**: Agents check inbox on startup
- 📊 **New CLI commands**: `message`, `channel` subcommands
- 📊 **Human role shift**: From "router" to "observer/moderator"

## Alternatives Considered

### Alternative 1: Platform-Based Communication (Original KIT-ADR-0021)

**Description**: Migrate to platform providing native message routing.

**Not chosen because**:
- Adds external dependency
- Requires learning new platform
- May not fit CLI-first workflow
- File-based approach achieves same goals with less complexity

### Alternative 2: WebSocket Server

**Description**: Build local WebSocket server for agent coordination.

**Not chosen because**:
- Requires running server process
- More infrastructure to maintain
- Over-engineered for file-based system

### Alternative 3: Keep Human as Router

**Description**: Maintain current manual relay approach.

**Not chosen because**:
- Doesn't scale
- Exhausting for human operator
- Introduces latency and potential miscommunication

## Success Metrics

### Quantitative

| Metric | Baseline | Target |
|--------|----------|--------|
| Human relay actions per session | ~20 | 0 |
| Agent-to-agent latency (file watcher) | N/A | < 5 seconds |
| Message loss rate | N/A | 0% |
| Human visibility coverage | 100% | 100% |

### Qualitative

- Agents coordinate effectively without human relay
- Human can observe and intervene when needed
- System feels natural for CLI-based development
- No new infrastructure burden

## Related Decisions

- KIT-ADR-0014: Code Review Workflow
- KIT-ADR-0019: Review Knowledge Extraction
- KIT-ADR-0021: Real-Time Agent Communication (original, superseded)

## References

- Miriad Research: `.agent-context/research/miriad/SYNTHESIS.md`
- Tymbal Protocol Analysis: `.agent-context/research/miriad/TYMBAL-PROTOCOL.md`
- sanity-labs/miriad-app: https://github.com/sanity-labs/miriad-app
- ULID Specification: https://github.com/ulid/spec

## Revision History

- 2026-02-05: KIT-ADR-0021-B created (Proposed)
  - Revised based on Miriad research (6 phases)
  - Changed from platform-based to file-based Tymbal variant
  - Added detailed error handling strategy
  - Added resource management options
  - Added testing requirements and acceptance criteria
  - Added 4-phase implementation plan

---

**Template Version**: 1.1.0
**Last Updated**: 2026-02-05
**Project**: agentive-starter-kit
