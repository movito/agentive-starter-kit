# Miriad-App Architecture Summary

**Date**: 2026-02-05
**Research Phase**: 1 (High-Level Architecture)
**Status**: Complete
**Repository**: https://github.com/sanity-labs/miriad-app

---

## Executive Summary

Miriad (also called "Cast") is a multi-agent collaboration platform from Sanity.io that enables multiple AI agents to work together on complex projects with human oversight. The system uses a custom **Tymbal Protocol** for real-time streaming communication and implements Sanity's **Nuum Memory Architecture** for long-running agent sessions.

**Key Insight**: Miriad is designed for **long-running agents** with continuous memory refinement, fundamentally different from our ephemeral agent model.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           MIRIAD PLATFORM                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────┐      ┌──────────────┐      ┌─────────────────────┐      │
│   │  Web UI  │◄────►│    Server    │◄────►│   PostgreSQL/Neon   │      │
│   │ (Studio) │      │   (Hono)     │      │     (Storage)       │      │
│   └──────────┘      └──────────────┘      └─────────────────────┘      │
│        │                   │                                            │
│        │                   │ Tymbal Protocol                            │
│        │                   ▼ (WebSocket + NDJSON)                       │
│        │            ┌──────────────┐                                    │
│        │            │   Runtime    │                                    │
│        │            │  (Container) │                                    │
│        │            └──────────────┘                                    │
│        │                   │                                            │
│        │                   │ @anthropic-ai/claude-agent-sdk            │
│        │                   ▼                                            │
│        │            ┌──────────────┐                                    │
│        └───────────►│ Claude Agent │◄──── MCP Tools                    │
│          (Human     │   (Nuum)     │                                    │
│          Oversight) └──────────────┘                                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Sanity Studio (React) | Human interface, board visualization |
| **API Server** | Hono | Lightweight web framework for API endpoints |
| **Database** | PostgreSQL via Neon | Persistent storage, message history |
| **Real-time** | WebSocket + NDJSON | Tymbal protocol transport |
| **Agent SDK** | @anthropic-ai/claude-agent-sdk | Claude integration |
| **Runtime** | Docker containers | Agent isolation |
| **Package Manager** | pnpm (monorepo) | Workspace management |
| **Type Safety** | TypeScript, Zod | Schema validation |
| **IDs** | ULID | Sortable unique identifiers |

---

## Package Structure (Backend Monorepo)

```
backend/packages/
├── core/           # Shared types, utilities, Tymbal protocol types
├── server/         # Hono-based API server
├── storage/        # PostgreSQL/Neon persistence layer
├── runtime/        # Agent runtime management
├── local-runtime/  # Local development runtime (uses claude-agent-sdk)
├── tunnel-server/  # External connectivity tunneling
└── assets-mcp/     # MCP server for asset management
```

### Key Dependencies

**From `local-runtime/package.json`**:
```json
{
  "@anthropic-ai/claude-agent-sdk": "latest",
  "@modelcontextprotocol/sdk": "^1.10.2",
  "eventsource-parser": "^3.0.1",
  "ws": "^8.18.2"
}
```

**Claude Integration**: Uses Anthropic's official `claude-agent-sdk` for agent operations, not raw API calls.

---

## Tymbal Protocol

Tymbal is a custom streaming protocol for agent communication.

### Transport Layer
- **WebSocket** for real-time bidirectional communication
- **NDJSON framing** (newline-delimited JSON)
- **HTTP fallback** for non-streaming operations

### Frame Types

| Frame Type | Purpose |
|------------|---------|
| `start` | Begin a new message |
| `append` | Add content to current message |
| `set` | Replace/set content |
| `control` | Control signals (heartbeat, close, etc.) |

### Message Types

| Type | Description |
|------|-------------|
| `User` | Human user message |
| `Agent` | Agent response message |
| `ToolCall` | Agent invoking a tool |
| `ToolResult` | Tool execution result |
| `Thinking` | Agent's internal reasoning (visible to humans) |
| `Status` | Status updates |
| `Error` | Error messages |
| `AgentComplete` | Agent finished task |
| `AgentMessage` | Agent-to-agent communication |

### Addressing
Messages include `agentId` and `boardId` for routing:
```typescript
interface TymbalFrame {
  type: 'start' | 'append' | 'set' | 'control';
  messageType: MessageType;
  agentId?: string;
  boardId?: string;
  content?: string;
  metadata?: Record<string, unknown>;
}
```

---

## Agent Architecture

### Agent Roles (from Miriad)
- **Lead** - Orchestrates other agents
- **Builder** - Implements code
- **Researcher** - Gathers information
- **Reviewer** - Reviews code/content
- **Designer** - Creates designs
- **Writer** - Creates documentation

### Agent Lifecycle
1. User @mentions an agent on a board
2. Server routes to Runtime
3. Runtime spawns container for agent
4. Agent initializes with `claude-agent-sdk`
5. Agent streams responses via Tymbal
6. Messages persisted to PostgreSQL
7. **Agent remains active** (long-running, not ephemeral)

### Memory Model (Nuum)

**Three-Tier Architecture**:

| Tier | Content | Persistence |
|------|---------|-------------|
| **Tier 1: Temporal** | Full message history | Session |
| **Tier 2: Distilled** | Narrative + Retained Facts | Recursive compression |
| **Tier 3: Long-Term** | Durable knowledge | Permanent |

**Key Mechanism**: Background distillation (not summarization) preserves operational intelligence while compressing context.

**Results**: 7,400+ messages over 6 days with maintained coherence.

---

## Data Flow

```
User Input                    Agent Response
    │                              ▲
    ▼                              │
┌─────────┐                  ┌─────────┐
│ Web UI  │──── HTTP ───────►│ Server  │
└─────────┘                  └────┬────┘
                                  │
                      Tymbal (WebSocket)
                                  │
                             ┌────▼────┐
                             │ Runtime │
                             └────┬────┘
                                  │
                      claude-agent-sdk
                                  │
                             ┌────▼────┐
                             │ Claude  │◄──── MCP Tools
                             └─────────┘
```

1. **Input**: User sends message via Web UI
2. **Routing**: Server identifies target agent by @mention
3. **Execution**: Runtime invokes agent in container
4. **Processing**: Claude processes via agent-sdk
5. **Streaming**: Response streamed via Tymbal
6. **Storage**: Messages persisted to PostgreSQL
7. **Display**: UI updates in real-time

---

## Human Visibility & Intervention

### Visibility
- All agent messages visible on shared "board"
- Thinking/reasoning visible (not hidden)
- Tool calls and results displayed
- Real-time streaming updates

### Intervention Points
- @mention to engage specific agent
- Direct messages to agents
- Ability to pause/redirect agents
- Human can take over tasks

### Permission Model
- Board-level access control
- Agent capabilities defined per role
- Tool access controlled via MCP

---

## Key Architectural Decisions

1. **Long-Running Agents**: Unlike ephemeral task-based agents, Miriad agents persist and maintain memory across many interactions.

2. **Custom Protocol (Tymbal)**: Built specifically for agent streaming rather than using existing protocols like JSON-RPC.

3. **Container Isolation**: Each agent runs in isolated container for security and resource management.

4. **Anthropic SDK**: Uses official claude-agent-sdk rather than raw API, getting benefits of Claude Code's tool system.

5. **Web-First**: Designed for browser-based human interaction, not CLI.

---

## Comparison: Miriad vs Agentive Starter Kit

| Aspect | Miriad | Agentive Starter Kit |
|--------|--------|---------------------|
| **Agent Lifecycle** | Long-running (days) | Ephemeral (task → exit) |
| **Memory** | 3-tier with distillation | Context compaction + file handoffs |
| **Human Interface** | Web browser | CLI (terminal) |
| **Communication** | Tymbal (WebSocket) | File-based + async |
| **Deployment** | Cloud platform | Local-first |
| **Agent SDK** | @anthropic-ai/claude-agent-sdk | Claude Code CLI |
| **Storage** | PostgreSQL | Filesystem |
| **Real-time** | Native WebSocket | Not implemented |

---

## Compatibility Assessment (Preliminary)

### What We Can Adopt
- ✅ Message type taxonomy (User, Agent, ToolCall, etc.)
- ✅ Board/workspace concept for shared context
- ✅ Thinking visibility pattern
- ✅ Some Tymbal concepts for future WebSocket implementation

### What Needs Adaptation
- ⚠️ Tymbal protocol → file-based equivalent for CLI
- ⚠️ Web UI → terminal-based visualization
- ⚠️ Container runtime → local process model
- ⚠️ PostgreSQL storage → filesystem-based

### Fundamental Differences
- ❌ Long-running vs ephemeral agents
- ❌ Browser vs CLI human interface
- ❌ Cloud-native vs local-first
- ❌ SDK-based vs CLI-based Claude integration

---

## Open Questions for Phase 2

1. **Can Tymbal work with ephemeral agents?** Or does it assume persistent connections?
2. **Is claude-agent-sdk available for non-Miriad use?** Could we adopt it?
3. **How does distillation trigger?** Time-based? Message count? Context %?
4. **What's the curator agent's logic?** For Tier 3 extraction.
5. **Can we implement file-based Tymbal?** Same concepts, different transport?

---

## Next Steps

**Phase 2: Agent Communication Deep-Dive**
- Study Tymbal protocol implementation details
- Understand message delivery guarantees
- Evaluate adopt vs adapt vs build decision
- Determine if ephemeral agents can use Tymbal concepts

**GO/NO-GO Decision Point**: After Phase 2, we'll have enough information to decide:
- **ADOPT**: Use Tymbal patterns directly
- **ADAPT**: Take concepts, build file-based implementation
- **ABORT**: Their approach doesn't fit our constraints

---

**Phase 1 Status**: ✅ Complete
**Recommendation**: Proceed to Phase 2 - this architecture has valuable patterns worth studying further, even if we can't adopt directly.
