# KIT-ADR-0021: Real-Time Agent Communication

**Status**: Proposed

**Date**: 2026-02-05

**Deciders**: movito, planner

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

### Forces at Play

**Technical Requirements:**
- Agents run as separate CLI processes (Claude Code)
- Each agent has distinct model, role, and MCP configuration
- Agents are currently stateless—they spin up, execute, and exit
- Human needs visibility into all agent conversations
- Human needs ability to intervene in any conversation

**Constraints:**
- Must work locally (no cloud dependencies required)
- Should integrate with existing file-based coordination
- Cannot modify Claude Code CLI internals
- Must preserve context-efficiency gains from current setup

**Assumptions:**
- Agents would need to become long-running (or frequently-polling) processes
- A shared communication channel is acceptable
- Message ordering and delivery guarantees can be eventual (not strict)

## Decision

We will adopt **platform-based communication** by migrating agent coordination to an environment that provides native message routing, with a **file-based message bus** as fallback for fully local operation.

### Core Principles

1. **Additive, not replacement**: Layer on top of existing file-based coordination
2. **Human as observer, not router**: Human can see all messages, intervene when needed
3. **Agents as peers**: Any agent can address any other agent
4. **Graceful degradation**: If message layer fails, fall back to manual handoffs

### Implementation Details

**Primary approach: Platform-based communication**

Migrate to a platform providing:
- Native message routing with @mentions
- Persistent shared artifacts (board)
- Agent presence and status
- Human visibility by default

**Key components:**

| Agentive Starter Kit | Platform Artifacts |
|---------------------|-------------------|
| `.claude/agents/*.md` | `system.agent` definitions |
| `delegation/tasks/*` | `task` artifacts with status |
| `docs/adr/*.md` | `doc` artifacts |
| `.agent-context/handoffs/` | artifact content + messages |
| `agent-handoffs.json` | `get_roster` + artifact status |

**Migration steps:**
1. Create agent definitions as `system.agent` artifacts
2. Import ADRs as `doc` artifacts
3. Model task lifecycle using `task` artifacts with status transitions
4. Use messages + @mentions for agent communication
5. Keep adversarial workflow as a `system.playbook`

**Fallback approach: File-based message bus**

For fully local operation without platform dependency:

```
.agent-context/
├── agent-handoffs.json      # Existing coordination
├── messages/
│   ├── inbox-planner.jsonl
│   ├── inbox-feature-developer.jsonl
│   ├── inbox-code-reviewer.jsonl
│   └── broadcast.jsonl
└── presence.json
```

**Message format:**
```json
{
  "id": "msg_01abc123",
  "ts": "2026-02-05T00:30:00Z",
  "from": "planner",
  "to": "feature-developer",
  "content": "Task ASK-0042 is ready for implementation.",
  "status": "unread"
}
```

**Agent polling wrapper:**
```bash
AGENT_NAME="feature-developer"
INBOX=".agent-context/messages/inbox-${AGENT_NAME}.jsonl"

while true; do
  UNREAD=$(jq -s '[.[] | select(.status == "unread")]' "$INBOX")
  if [ "$(echo $UNREAD | jq length)" -gt 0 ]; then
    MSG_TEXT=$(echo $UNREAD | jq -r '.[] | "@\(.from): \(.content)"')
    tmux send-keys -t "$AGENT_NAME" "$MSG_TEXT" Enter
  fi
  sleep 5
done
```

## Consequences

### Positive

- ✅ **Direct agent communication**: Agents can address each other without human relay
- ✅ **Human visibility preserved**: All messages visible, intervention always possible
- ✅ **Context efficiency maintained**: Existing patterns (Serena, handoffs) still work
- ✅ **New workflows enabled**: Agent debates, parallel reviews, real-time collaboration

### Negative

- ⚠️ **Resource usage**: Agents must become long-running or frequently-polling processes
- ⚠️ **New failure modes**: Message delivery, ordering, and presence become concerns
- ⚠️ **Platform dependency**: Primary approach requires adopting new environment
- ⚠️ **Latency tradeoff**: File-based fallback has 5+ second polling delay

### Neutral

- 📊 **Launch process changes**: Agents launched via wrapper scripts or platform spawn
- 📊 **Human role shift**: From "router" to "observer/moderator"
- 📊 **Surfaced bugs**: May expose coordination issues previously hidden by manual relay

## Alternatives Considered

### Alternative 1: Keep Human as Router

**Description**: Maintain current setup where human relays all inter-agent messages.

**Rejected because**:
- ❌ Doesn't scale (human becomes bottleneck)
- ❌ Exhausting for human operator
- ❌ Introduces latency and potential miscommunication
- ❌ Prevents agents from developing natural collaboration patterns

### Alternative 2: Modify Claude Code CLI

**Description**: Fork or extend Claude Code to add IPC/messaging capabilities.

**Rejected because**:
- ❌ Significant engineering effort
- ❌ Maintenance burden as upstream evolves
- ❌ Not portable to other agent runtimes

### Alternative 3: Lightweight Local Server

**Description**: Build custom WebSocket server for agent coordination.

**Rejected because**:
- ❌ More infrastructure to build and maintain
- ❌ Wrapper complexity for Claude CLI integration
- ❌ Platform-based option provides this without custom development

## Real-World Results

**Before this decision:**
- Human relay time: ~30-60 seconds per handoff
- Agent collaboration: Sequential only
- Human fatigue: High during multi-agent sessions

**After this decision:**
- (To be measured after implementation)

**Impact:**
- (To be documented after implementation)

## Related Decisions

- KIT-ADR-0014: Code Review Workflow
- KIT-ADR-0019: Review Knowledge Extraction

## References

- Agentive Starter Kit: https://github.com/movito/agentive-starter-kit
- Adversarial Workflow: https://github.com/movito/adversarial-workflow

## Revision History

- 2026-02-05: Initial proposal (Proposed)
  - Documented platform-based and file-based implementation options
  - Recommended platform approach with file-based fallback

---

**Template Version**: 1.1.0
**Last Updated**: 2026-02-05
**Project**: agentive-starter-kit
