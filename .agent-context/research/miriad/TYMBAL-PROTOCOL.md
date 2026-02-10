# Tymbal Protocol Deep-Dive Analysis

**Date**: 2026-02-05
**Research Phase**: 2 (Agent Communication Deep-Dive)
**Status**: Complete
**Decision**: ADAPT (not ADOPT or ABORT)

---

## Executive Summary

Tymbal is Miriad's custom streaming protocol for real-time agent communication. After deep analysis, the conclusion is:

**ADAPT**: We cannot adopt Tymbal directly (requires persistent connections and long-running agents), but we can adapt its message taxonomy and routing concepts for a file-based implementation suitable for our ephemeral agent model.

---

## Protocol Specification

### Transport Layer

| Aspect | Tymbal Specification |
|--------|---------------------|
| **Primary** | WebSocket (bidirectional) |
| **Framing** | NDJSON (newline-delimited JSON) |
| **Fallback** | HTTP for non-streaming operations |
| **Authentication** | Bearer token or API key (HTTP header) |
| **Connection** | Persistent, with reconnection support |

### Connection Lifecycle

```
Client ────► WebSocket Connect to /threads/{threadId}/stream
         ◄──── Server accepts (even before thread exists)

Client ────► {request: "sync"} (optional, for reconnection)
Server ◄──── Historical frames
Server ◄──── In-progress frames via append
Server ◄──── Finalizing set frames

         ... bidirectional streaming ...

Server ────► Close code 1000 (normal) / 4004 (not found) / 4009 (complete)
```

### Frame Types (5 categories)

| Frame | Format | Purpose |
|-------|--------|---------|
| **Start** | `{"i":"<ulid>"}` or `{"i":"<ulid>","m":<metadata>}` | Begin new message |
| **Append** | `{"i":"<ulid>","a":"<string>"}` | Add content progressively |
| **Set** | `{"i":"<ulid>","t":"<timestamp>","v":<object>}` | Complete/replace message |
| **Sync** | `{"request":"sync","since":"<timestamp>"}` | Request history |
| **Error** | `{"error":"<code>","message":"<description>"}` | Communicate failures |

### Message Ordering

- **No sequence numbers** - uses ULID lexicographic sort
- Frames may arrive interleaved across messages
- Client reconstructs order by sorting message IDs
- Timestamps (ISO 8601) used for sync filtering

---

## Message Types (9 total)

### Core Messages (5)

| Type | Direction | Streaming | Purpose |
|------|-----------|-----------|---------|
| **User** | Human → Agent | No | User input |
| **Agent** | Agent → Human | Yes | Agent responses |
| **ToolCall** | Agent → System | Yes | Tool invocation |
| **ToolResult** | System → Agent | No | Tool outcome |
| **Thinking** | Agent internal | Yes | Reasoning (visible) |

### Multi-Agent Extensions (4)

| Type | Purpose |
|------|---------|
| **Status** | Transient work indicator |
| **Error** | User-facing errors (distinct from tool errors) |
| **AgentComplete** | Sub-agent completion signal |
| **AgentMessage** | Agent-to-agent communication |

### Message Flow Pattern

```
User Input
    │
    ▼
┌─────────┐
│Thinking │ (optional, visible)
└────┬────┘
     │
     ▼
┌──────────┐    ┌────────────┐
│ToolCall  │───►│ ToolResult │
└──────────┘    └─────┬──────┘
                      │
                      ▼
              ┌───────────┐
              │   Agent   │ (response)
              └───────────┘
```

---

## Message Routing

### Mention-Based Addressing

```typescript
// Example: @builder @reviewer please check this code
getAddressedAgents(content) → ['builder', 'reviewer']
```

### Routing Rules

| Pattern | Behavior |
|---------|----------|
| `@agentname` | Direct to specific agent |
| `@channel` | Broadcast to all roster agents |
| No mentions | Seen only by sender |

### Visibility Scoping

Agents see messages only when:
1. They are explicitly `@mentioned`
2. They are the sender
3. Message is a `@channel` broadcast

**Critical**: This prevents unintended message exposure between agents.

---

## Agent Lifecycle Requirements

### State Machine

```
┌─────────┐
│ offline │ (initial / suspended)
└────┬────┘
     │ activate()
     ▼
┌───────────┐
│activating │
└─────┬─────┘
      │ ready
      ▼
┌─────────┐◄───────────┐
│ online  │            │
└────┬────┘            │
     │ message         │ complete
     ▼                 │
┌─────────┐────────────┘
│  busy   │
└─────────┘
```

### Key Characteristics

| Aspect | Miriad Behavior |
|--------|-----------------|
| **Persistence** | Long-running within session |
| **State Storage** | In-memory Map<string, AgentInstance> |
| **Auto-recovery** | Offline agents auto-reactivate on message |
| **Mid-turn injection** | Messages can be pushed during execution |
| **Heartbeat** | Every 30 seconds for liveness |
| **Idle timeout** | Exit when no agents processing |

### Reconnection Strategy

```
Disconnect detected
    │
    ├── Wait 1s, retry
    │   └── Fail → Wait 2s, retry
    │             └── Fail → Wait 4s, retry
    │                       └── Fail → Wait 8s, retry
    │                                 └── Fail → Wait 16s, retry
    │                                           └── Fail → Wait 30s (max), retry
    │
    └── Success → Re-check-in all active agents
```

---

## Delivery Guarantees

| Guarantee | Status |
|-----------|--------|
| **Ordering** | ULID-based (client reconstructs) |
| **At-least-once** | Via sync on reconnect |
| **At-most-once** | Not guaranteed (duplicates possible) |
| **Exactly-once** | Not provided |
| **Cancellation** | Best-effort (may not interrupt mid-processing) |

### Error Handling

| Error Code | Meaning |
|------------|---------|
| `invalid_request` | Malformed request |
| `thread_not_found` | Unknown thread ID |
| `rate_limited` | Too many requests (429) |
| WebSocket 4004 | Thread not found |
| WebSocket 4009 | Thread completed/cancelled |

---

## Compatibility Analysis

### Fundamental Differences

| Aspect | Tymbal (Miriad) | Agentive Starter Kit |
|--------|-----------------|---------------------|
| **Connection** | Persistent WebSocket | None (file-based) |
| **Agent Lifecycle** | Long-running (days) | Ephemeral (task → exit) |
| **State** | In-memory + distillation | File handoffs |
| **Human Interface** | Web browser | CLI terminal |
| **Transport** | Real-time streaming | Async file I/O |
| **Server** | Required (Hono/PostgreSQL) | Optional |

### Cannot Adopt Directly Because:

1. **Persistent Connections Required**: Tymbal assumes WebSocket stays open
2. **Long-Running Agents Assumed**: State transitions (offline→online→busy) require continuity
3. **Server Infrastructure**: Needs backend for routing, storage, sync
4. **Web Interface**: Designed for browser rendering, not CLI

### Can Adapt These Concepts:

1. **Message Taxonomy**: User, Agent, ToolCall, ToolResult, Thinking types
2. **Mention Routing**: `@agent` addressing pattern
3. **Visibility Scoping**: Agents see only their messages
4. **Frame Concept**: Start/Append/Set for progressive updates
5. **ULID Ordering**: Sortable IDs without sequence numbers

---

## ADOPT/ADAPT/ABORT Decision

### Decision: **ADAPT**

Build a **file-based Tymbal variant** that:
- Uses the same message type taxonomy
- Implements mention-based routing via file naming/metadata
- Provides visibility scoping through file organization
- Supports ephemeral agents (read on start, write on exit)
- Works without persistent connections or server infrastructure

### Rationale

| Option | Analysis |
|--------|----------|
| **ADOPT** | ❌ Impossible - requires persistent connections, long-running agents, server infrastructure |
| **ADAPT** | ✅ Viable - message concepts are transport-agnostic |
| **ABORT** | ❌ Wasteful - valuable patterns worth preserving |

### What We Gain by Adapting

1. **Proven message taxonomy** - 9 message types cover all agent communication needs
2. **Visibility model** - Scoped messaging prevents information overload
3. **Routing pattern** - `@mention` is intuitive for both humans and agents
4. **Thinking visibility** - Human oversight without intrusion

### What We Build Differently

| Tymbal | File-Based Variant |
|--------|-------------------|
| WebSocket frames | NDJSON log files |
| In-memory state | File-based handoffs |
| Real-time streaming | Poll-on-read |
| PostgreSQL persistence | Filesystem |
| Web UI broadcast | Terminal tail/watch |

---

## Proposed File-Based Protocol

### Directory Structure

```
.agent-context/channels/
├── main/                    # Default channel
│   ├── messages.ndjson      # Append-only message log
│   ├── roster.json          # Active agents
│   └── artifacts/           # Shared artifacts
└── feature-xyz/             # Feature-specific channel
    ├── messages.ndjson
    ├── roster.json
    └── artifacts/
```

### Message Format (adapted from Tymbal)

```json
{"id":"01HX...","t":"2026-02-05T10:30:00.000Z","type":"user","sender":"human","content":"@builder please implement the login feature","addressed":["builder"]}
{"id":"01HX...","t":"2026-02-05T10:30:05.000Z","type":"thinking","sender":"builder","content":"Analyzing login requirements..."}
{"id":"01HX...","t":"2026-02-05T10:30:10.000Z","type":"tool_call","sender":"builder","toolCallId":"tc_1","name":"Read","arguments":{"file_path":"src/auth.py"}}
{"id":"01HX...","t":"2026-02-05T10:30:11.000Z","type":"tool_result","toolCallId":"tc_1","status":"success","output":"...file content..."}
{"id":"01HX...","t":"2026-02-05T10:30:30.000Z","type":"agent","sender":"builder","content":"I've analyzed the auth module...","addressed":["human"]}
```

### Ephemeral Agent Flow

```
Agent Starts
    │
    ├── Read roster.json (am I active?)
    ├── Read messages.ndjson (filter to my @mentions)
    ├── Process relevant messages
    ├── Append responses to messages.ndjson
    └── Exit (handoff via file, not memory)

Next Agent Starts
    │
    ├── Read roster.json
    ├── Read messages.ndjson (since last timestamp)
    └── ... continues ...
```

---

## Next Steps

1. **Phase 3**: Study Miriad's Shared Board / Artifact system
2. **Prototype**: Build minimal file-based message log
3. **Test**: Verify ephemeral agents can coordinate via files
4. **Document**: Update KIT-ADR-0021 with ADAPT decision

---

## Open Questions

- [ ] How to handle concurrent writes to messages.ndjson?
- [ ] What's the polling interval for CLI "watch" mode?
- [ ] Should artifacts be versioned or append-only?
- [ ] How to implement `@channel` broadcast for CLI?

---

**Phase 2 Status**: ✅ Complete
**Decision**: ADAPT - Build file-based variant using Tymbal concepts
**Confidence**: HIGH - Message taxonomy is transport-agnostic, ephemeral model is viable
