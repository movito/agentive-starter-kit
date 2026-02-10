# Miriad Research Synthesis & Recommendations

**Date**: 2026-02-05
**Research Phase**: 6 (Final Synthesis)
**Status**: Complete
**Purpose**: Inform revision of KIT-ADR-0021

---

## Executive Summary

After comprehensive analysis of sanity-labs/miriad-app across 5 phases, we recommend **ADAPT** - taking Miriad's proven patterns and adapting them for our ephemeral, CLI-first, file-based architecture.

### Key Decision

| Aspect | Miriad Approach | Our Adaptation |
|--------|-----------------|----------------|
| **Transport** | WebSocket (persistent) | File-based (NDJSON logs) |
| **Agent Lifecycle** | Long-running (days) | Ephemeral (task → exit) |
| **Human Interface** | Web browser | CLI terminal |
| **Storage** | PostgreSQL | Filesystem + Git |
| **Communication** | Tymbal protocol | File-based Tymbal variant |

### Bottom Line

We cannot adopt Miriad directly (requires persistent connections, long-running agents, server infrastructure). However, their **message taxonomy**, **routing patterns**, and **artifact organization** are transport-agnostic and directly applicable to our file-based approach.

---

## Research Summary

### Phase 1: Architecture

**Finding**: Miriad is a pnpm monorepo with Hono API server, PostgreSQL storage, WebSocket real-time, and containerized agent runtime.

**Relevance**: Their modular architecture separates concerns cleanly. We can apply similar separation (protocol ↔ transport ↔ storage).

### Phase 2: Tymbal Protocol (ADAPT Decision)

**Finding**: Tymbal is NDJSON-framed streaming with 5 frame types and 9 message types. Uses ULID ordering, eventual consistency, mention-based routing.

**Relevance**:
- ✅ Message taxonomy (User, Agent, ToolCall, ToolResult, Thinking) - directly adoptable
- ✅ @mention routing - adaptable to file naming
- ✅ NDJSON framing - works for file-based logs
- ❌ Persistent WebSocket - requires adaptation

### Phase 3: Artifacts & Shared Board

**Finding**: 12 artifact types with status workflows, CAS updates, versioning, cross-references.

**Relevance**:
- ✅ Artifact types (doc, task, decision, code) - we already use equivalents
- ✅ Status workflow (pending → in_progress → done) - matches our folder system
- ✅ Cross-references via `refs` field - adoptable for dependency tracking
- ⚠️ CAS updates - Git provides equivalent via merge conflicts

### Phase 4: Agent Definitions

**Finding**: Agents defined as `system.agent` artifacts with engine, MCP servers, identity. Pluggable engine system (claude-sdk, nuum).

**Relevance**:
- ✅ Structured agent metadata - enhance our `.claude/agents/*.md` files
- ✅ MCP server configuration - adopt their format
- ⚠️ Engine abstraction - future consideration
- ❌ Long-running lifecycle - doesn't fit ephemeral model

### Phase 5: Claude Integration

**Finding**: Uses `@anthropic-ai/claude-agent-sdk` with session resume/fork, MCP integration, permission modes.

**Relevance**:
- ✅ Session management concepts - adapt for file-based sessions
- ✅ MCP configuration format - directly adoptable
- ✅ Permission modes - inform our tool access patterns
- ⚠️ SDK vs CLI - consider SDK for future orchestration

---

## Gap Analysis

### Current Agentive Starter Kit

| Feature | Implementation | Limitation |
|---------|---------------|------------|
| **Agent Communication** | Manual via human relay | Bottleneck, doesn't scale |
| **Message Format** | Unstructured handoff docs | No standard taxonomy |
| **Routing** | Implicit via file location | No direct addressing |
| **Session Continuity** | Context compaction | No resume/fork capability |
| **Artifact References** | Ad-hoc mentions | No formal dependency tracking |
| **Real-time Updates** | None | Human polls terminals |

### Miriad Capabilities We Lack

| Capability | Miriad | Gap |
|------------|--------|-----|
| Direct @mention routing | ✅ | Missing |
| Structured message taxonomy | ✅ 9 types | Missing |
| Visibility scoping | ✅ Agents see only their messages | Missing |
| Session resume/fork | ✅ | Missing |
| Cross-references | ✅ `refs` field | Partial (no formal system) |
| Real-time streaming | ✅ WebSocket | Not applicable (CLI) |

### Our Advantages

| Feature | Our Approach | Benefit |
|---------|--------------|---------|
| **Simplicity** | File-based, no server | Easy setup, portable |
| **Git Integration** | Native versioning | History, branches, diffs |
| **CLI-first** | Terminal workflows | Developer-friendly |
| **Ephemeral Agents** | Task-focused | Lower resource usage |
| **Offline-capable** | No cloud dependency | Works anywhere |

---

## Pattern Catalog

### ADOPT (Use Directly)

| Pattern | Source | Application |
|---------|--------|-------------|
| **Message Type Taxonomy** | Tymbal Protocol | User, Agent, ToolCall, ToolResult, Thinking, Status, Error |
| **NDJSON Framing** | Tymbal Protocol | Append-only log files |
| **ULID Ordering** | Tymbal Protocol | Sortable IDs without sequence numbers |
| **@mention Syntax** | Message Routing | `@agent-name` for addressing |
| **MCP Config Format** | Agent Definition | Structured MCP server configuration |
| **Artifact Status** | Shared Board | pending, in_progress, done, blocked |
| **Cross-References** | Artifact Model | `refs:` field for dependencies |

### ADAPT (Modify for Our Use)

| Pattern | Miriad | Our Adaptation |
|---------|--------|----------------|
| **Channel/Board** | WebSocket + PostgreSQL | Directory + NDJSON files |
| **Real-time Updates** | WebSocket broadcast | File watcher + terminal notify |
| **Session Persistence** | In-memory + distillation | File-based session IDs |
| **Agent Roster** | Database table | `roster.json` file |
| **Visibility Scoping** | Server-side filtering | Agent filters own messages on read |
| **Sync Protocol** | Sync frames over WebSocket | Git pull + timestamp filtering |

### SKIP (Not Applicable)

| Pattern | Reason |
|---------|--------|
| **Long-running Agents** | Conflicts with ephemeral model |
| **Mid-turn Injection** | Requires persistent connection |
| **Three-tier Memory** | Complex, requires background workers |
| **Container Isolation** | Over-engineered for CLI use |
| **WebSocket Transport** | Requires server infrastructure |

---

## Addressing Evaluator Concerns

The evaluator flagged KIT-ADR-0021 as NEEDS_REVISION with these concerns:

### CRITICAL: Error Handling for Message Delivery

**Evaluator concern**: "Lacks detailed error handling for message delivery failures or ordering issues."

**Miriad's solution**: ULID ordering + sync-on-reconnect + eventual consistency.

**Our adaptation**:

```
Error Handling Strategy (File-Based)
────────────────────────────────────

1. ORDERING
   - Use ULID for message IDs (lexicographically sortable)
   - Sort by ID on read, not arrival time
   - No sequence numbers needed

2. DELIVERY FAILURES
   - Append-only logs (no delivery = no append)
   - Agent reads all unread messages on startup
   - Idempotent message processing (ID-based dedup)

3. CONSISTENCY
   - Eventual consistency is acceptable (per assumptions)
   - Git provides sync mechanism for distributed scenarios
   - Conflict resolution via merge, not prevention

4. RECOVERY
   - Messages persisted to filesystem (durable)
   - Agent can resume from any point using timestamp filter
   - No message loss unless filesystem fails
```

### MEDIUM: Resource Usage (Long-Running Processes)

**Evaluator concern**: "Agents becoming long-running processes could impact system performance."

**Miriad's approach**: Long-running with distillation + idle timeout (15 min).

**Our adaptation**:

```
Resource Management Strategy
────────────────────────────

Option A: EPHEMERAL (Recommended)
- Agents remain ephemeral (task → exit)
- Messages buffered in files while agent offline
- Agent reads inbox on startup, processes, exits
- No polling, no idle processes
- Lowest resource usage

Option B: POLLING (For Real-Time)
- Agent polls inbox every N seconds
- Configurable interval (5s default)
- Idle timeout: exit after M minutes of no messages
- Resource: 1 process per active agent

Option C: FILE WATCHER (Middle Ground)
- Agent uses fswatch/inotify on inbox
- No polling, event-driven
- Exit on idle timeout
- Resource: 1 process + 1 watcher per agent

Recommendation: Start with Option A (ephemeral).
Add Option C (file watcher) for agents needing faster response.
```

### LOW: Testing Strategy

**Evaluator concern**: "Does not address how to test the new communication system."

**Our response**:

```
Testing Strategy
────────────────

1. UNIT TESTS
   - Message parsing/serialization
   - ULID generation and sorting
   - Mention extraction (@agent patterns)
   - Inbox filtering logic

2. INTEGRATION TESTS
   - Agent A writes → Agent B reads
   - Broadcast to all agents
   - Message ordering preserved across writes

3. SCENARIO TESTS
   - Planner → Feature-Developer handoff
   - Code-Reviewer → Feature-Developer feedback loop
   - Multi-agent debate (3+ agents)

4. FAILURE TESTS
   - Concurrent writes to same log
   - Agent crash during processing
   - Malformed message handling
   - Large message handling

5. ACCEPTANCE CRITERIA
   - Messages delivered within 1 second (file watcher mode)
   - Messages preserved across agent restarts
   - Human can read all messages via CLI
   - No message loss under normal operation
```

### Missing: File/Function Names

**Our response**: See Implementation Roadmap below with specific file locations and functions.

---

## Revised ADR Recommendations

### Update KIT-ADR-0021 with:

1. **Concrete file-based protocol** (not just fallback)
2. **Error handling strategy** from Miriad learnings
3. **Resource management options** (ephemeral/polling/watcher)
4. **Testing requirements** and acceptance criteria
5. **Implementation phases** with specific deliverables

### Key Changes to ADR

| Section | Current | Recommended |
|---------|---------|-------------|
| **Primary Approach** | "Platform-based communication" | "File-based Tymbal variant" |
| **Fallback** | File-based as fallback | Platform as future enhancement |
| **Message Format** | Basic JSON | Full Tymbal message types |
| **Error Handling** | Not specified | ULID ordering, dedup, recovery |
| **Resource Model** | "Long-running or polling" | Ephemeral-first, watcher optional |
| **Testing** | Not specified | Unit/integration/scenario tests |

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)

**Goal**: Establish message format and basic infrastructure

**Deliverables**:

```
.agent-context/
├── channels/
│   └── main/
│       ├── messages.ndjson    # Append-only message log
│       └── roster.json        # Active agents
└── lib/
    ├── message.py             # Message class + serialization
    ├── channel.py             # Channel read/write operations
    └── ulid.py                # ULID generation (or use package)
```

**Functions**:
```python
# message.py
class Message:
    id: str          # ULID
    timestamp: str   # ISO 8601
    type: MessageType  # user, agent, tool_call, tool_result, thinking, status, error
    sender: str      # Agent callsign or "human"
    content: str
    addressed: list[str]  # @mentioned agents
    refs: list[str]  # Related message/artifact IDs

def parse_mentions(content: str) -> list[str]
def create_message(type, sender, content, addressed=None) -> Message
def serialize(message: Message) -> str  # NDJSON line
def deserialize(line: str) -> Message

# channel.py
def append_message(channel: str, message: Message) -> None
def read_messages(channel: str, since: str = None) -> list[Message]
def filter_for_agent(messages: list, agent: str) -> list[Message]
def get_roster(channel: str) -> list[RosterEntry]
def update_roster(channel: str, agent: str, status: str) -> None
```

**Tests**:
- `tests/test_message.py`
- `tests/test_channel.py`

### Phase 2: Agent Integration (Week 2)

**Goal**: Enable agents to send/receive messages

**Deliverables**:

```
scripts/
├── agent-wrapper.sh           # Wraps agent with inbox check
└── project (updated)
    └── message command        # CLI for sending messages
```

**Agent Startup Flow**:
```
1. Agent starts
2. Read roster.json, update own status to "active"
3. Read messages.ndjson, filter to own @mentions
4. Process unread messages (inject into prompt)
5. Work on task
6. On message to send: append to messages.ndjson
7. On exit: update roster status to "offline"
```

**CLI Commands**:
```bash
./scripts/project message send @feature-developer "Task ready"
./scripts/project message list --channel main --since 1h
./scripts/project message inbox feature-developer
```

### Phase 3: Human Interface (Week 3)

**Goal**: Enable human observation and participation

**Deliverables**:

```
scripts/
├── channel-watch.sh           # Real-time message display
└── project (updated)
    └── channel commands       # List, join, observe
```

**Human Capabilities**:
```bash
# Watch channel in real-time
./scripts/project channel watch main

# Send message as human
./scripts/project message send @planner "Please prioritize ASK-0050"

# View agent roster
./scripts/project channel roster main
```

**Display Format** (terminal):
```
[10:30:05] @human → @planner
  Please prioritize ASK-0050

[10:30:08] @planner → @feature-developer
  🤔 Analyzing task priorities...

[10:30:15] @planner → @feature-developer
  Task ASK-0050 is now top priority. See delegation/tasks/2-todo/ASK-0050.md
```

### Phase 4: Enhanced Features (Week 4)

**Goal**: Add cross-references, dependency tracking, enhanced metadata

**Deliverables**:

```
# Enhanced task frontmatter
---
id: ASK-0050
type: task
status: in_progress
assignees: [feature-developer]
refs:
  - KIT-ADR-0021
  - ASK-0042
labels: [agent-communication, priority-high]
channel: main
---
```

**Dependency CLI**:
```bash
./scripts/project task deps ASK-0050
./scripts/project task refs KIT-ADR-0021
```

---

## Success Metrics

### Quantitative

| Metric | Baseline | Target |
|--------|----------|--------|
| Human relay actions per session | ~20 | 0 |
| Agent-to-agent message latency | N/A | < 5 seconds |
| Messages lost | N/A | 0 |
| Human visibility coverage | 100% | 100% |

### Qualitative

- [ ] Agents can coordinate without human relay
- [ ] Human can observe all agent communication
- [ ] Human can intervene at any point
- [ ] System works fully offline
- [ ] No new server infrastructure required

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Concurrent write conflicts | Use atomic append (file locking) |
| Message ordering bugs | ULID sorting, comprehensive tests |
| Agent doesn't check inbox | Require inbox check in agent startup |
| Inbox grows unbounded | Archival after N days, compaction |
| Human misses important messages | Priority flag, filtering by importance |

---

## Research Artifacts

| Document | Content | Location |
|----------|---------|----------|
| ARCHITECTURE.md | System overview, tech stack | `.agent-context/research/miriad/` |
| TYMBAL-PROTOCOL.md | Protocol deep-dive, ADAPT decision | `.agent-context/research/miriad/` |
| SHARED-BOARD-ARTIFACTS.md | Artifact types, status workflows | `.agent-context/research/miriad/` |
| AGENT-DEFINITIONS.md | Agent config, engine architecture | `.agent-context/research/miriad/` |
| CLAUDE-INTEGRATION.md | SDK analysis, session management | `.agent-context/research/miriad/` |
| NUUM-MEMORY-ARCHITECTURE.md | Memory tiers, distillation | `.agent-context/research/miriad/` |

---

## Conclusion

Miriad demonstrates that real-time multi-agent communication is achievable and valuable. Their architecture, while requiring persistent connections and server infrastructure, provides proven patterns we can adapt:

1. **Message taxonomy** - 9 types cover all communication needs
2. **@mention routing** - Intuitive addressing for humans and agents
3. **ULID ordering** - Sortable without coordination
4. **Eventual consistency** - Acceptable for our use case
5. **Visibility scoping** - Agents see only relevant messages

By building a **file-based Tymbal variant**, we get the benefits of structured agent communication while preserving our CLI-first, file-based, ephemeral-agent architecture.

**Next Steps**:
1. Revise KIT-ADR-0021 with these recommendations
2. Run evaluation on revised ADR
3. Create implementation task (ASK-00XX)
4. Begin Phase 1 implementation

---

**Research Status**: ✅ Complete
**Recommendation**: Revise KIT-ADR-0021 with file-based Tymbal variant, then implement in 4-week phases
**Confidence**: HIGH - Miriad patterns are proven, adaptation is straightforward
