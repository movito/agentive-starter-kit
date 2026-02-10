# Agent Definitions & Roles Analysis

**Date**: 2026-02-05
**Research Phase**: 4 (Agent Definitions & Roles)
**Status**: Complete

---

## Executive Summary

Miriad defines agents as **system artifacts** (`system.agent`) with pluggable engines, MCP tool access, and dynamic configuration. Their agent model is more flexible than ours but shares similar concepts - we can adopt their definition patterns while keeping our file-based approach.

**Key Insight**: Their `system.agent` artifact pattern maps well to our `.claude/agents/*.md` files. We can enhance our agent definitions with structured metadata.

---

## Agent Definition Format

### system.agent Schema

```typescript
interface SystemAgentProps {
  // Required
  engine: string;              // "claude-sdk" | "nuum" | custom

  // Optional
  model?: string;              // e.g., "claude-sonnet-4-20250514"
  nameTheme?: string;          // For generating callsigns
  agentName?: string;          // Fixed name for singleton agents
  mcp?: McpReference[];        // MCP server references
  featuredChannelStarter?: boolean;  // Show in new channel suggestions
}

interface McpReference {
  slug: string;                // Reference to system.mcp artifact
}
```

### Agent as Artifact

Agents are stored as artifacts with:
- **Type**: `system.agent`
- **Slug**: URL-safe identifier (e.g., `builder`, `researcher`)
- **Props**: Configuration from schema above
- **Content**: Optional markdown description/documentation

---

## Engine Architecture

### Pluggable Engine System

```
┌─────────────────────────────────────────────────┐
│               EngineManager                      │
├─────────────────────────────────────────────────┤
│  register(engine: AgentEngine)                   │
│  spawn(engineId, config) → EngineProcess         │
└─────────────────────────────────────────────────┘
          │                    │
          ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│ ClaudeSDKEngine │  │   NuumEngine    │
│ (claude-sdk)    │  │   (nuum)        │
└─────────────────┘  └─────────────────┘
```

### Engine Interface

Every engine implements:

```typescript
interface AgentEngine {
  engineId: string;           // Unique identifier
  displayName: string;        // Human-readable name

  spawn(config: EngineConfig): EngineProcess;
  isAvailable(): boolean;     // Check dependencies
}
```

### Engine Configuration

```typescript
interface EngineConfig {
  agentId: string;            // space:channel:callsign
  workspacePath: string;      // Isolated filesystem path
  systemPrompt: string;       // Initial instructions
  mcpServers: Record<string, McpServerConfig>;
  environment: Record<string, string>;
  engineOptions?: unknown;    // Engine-specific options
}
```

### Engine Process

```typescript
interface EngineProcess {
  pid: number | null;         // OS process ID (null for in-process)
  state: EngineState;         // starting | ready | busy | terminated

  send(message: UserMessage | ControlAction): void;
  output: AsyncIterable<SDKMessage>;
  terminate(): Promise<void>;
  onExit(handler: () => void): void;
}
```

---

## Available Engines

### 1. ClaudeSDKEngine

- **ID**: `claude-sdk`
- **Backend**: `@anthropic-ai/claude-agent-sdk`
- **Mode**: In-process or subprocess
- **Features**: Native Claude Code tools, MCP support

### 2. NuumEngine

- **ID**: `nuum`
- **Backend**: Custom Sanity implementation
- **Mode**: Subprocess (Bun runtime)
- **Features**: Three-tier memory, distillation, long-running sessions

---

## Agent Lifecycle

### State Machine

```
                    ┌───────────┐
                    │  offline  │ (initial state)
                    └─────┬─────┘
                          │ activate()
                          ▼
                    ┌───────────┐
                    │activating │ (starting engine)
                    └─────┬─────┘
                          │ ready
                          ▼
    ┌──────────────►┌───────────┐◄──────────────┐
    │               │  online   │               │
    │               └─────┬─────┘               │
    │                     │ message             │
    │                     ▼                     │
    │               ┌───────────┐               │
    └───────────────│   busy    │───────────────┘
       complete     └───────────┘
```

### Activation Flow

1. **Parse Agent ID**: `spaceId:channelId:callsign`
2. **Determine Engine**: From props (default: `claude-sdk`)
3. **Create Workspace**: `basePath/spaceId/channelId/callsign/`
4. **Instantiate Agent**: Create `AgentInstance` with state + bridge
5. **Spawn Engine**: Start subprocess or in-process

### AgentInstance Structure

```typescript
interface AgentInstance {
  agentId: string;
  state: AgentState;          // Status + timestamps
  bridge: TymbalBridge;       // Message translation
  engine: EngineProcess;
  messageStream?: MessageStream;  // For mid-turn injection
}
```

---

## Tool Access via MCP

### MCP Server Definition

```typescript
// system.mcp artifact props
interface SystemMcpProps {
  transport: 'stdio' | 'http';

  // For stdio transport
  command?: string;
  args?: string[];
  cwd?: string;
  variables?: Record<string, string>;

  // For http transport
  url?: string;
  oauth?: OAuthConfig;

  // Shared
  capabilities?: { description?: string };
}
```

### Tool Discovery & Execution

```
Agent                    MCP Endpoint                 MCP Server
  │                          │                            │
  │── tools/list ───────────►│                            │
  │                          │── forward ────────────────►│
  │                          │◄── tool definitions ───────│
  │◄── tool list ────────────│                            │
  │                          │                            │
  │── tools/call(name, args)►│                            │
  │                          │── execute ────────────────►│
  │                          │◄── result ─────────────────│
  │◄── tool result ──────────│                            │
```

### MCP Endpoint

- **Route**: `POST /mcp/:channel`
- **Protocol**: JSON-RPC 2.0
- **Methods**: `tools/list`, `tools/call`
- **Features**:
  - Variable expansion (`${VAR}` in configs)
  - Docker URL rewriting (`localhost` → `host.docker.internal`)
  - Context injection (storage, IDs, connection manager)

---

## Context Passing

### System Prompt Injection

System prompts are passed via `EngineConfig.systemPrompt` and can be updated per-message:

```typescript
// During activation
const config: EngineConfig = {
  systemPrompt: artifact.content || defaultPrompt,
  // ...
};

// Per-turn update
agent.updateSystemPrompt(newPrompt);
```

### Environment Variables

```typescript
const environment = {
  ...processEnvFiltered,      // Exclude PWD, OLDPWD
  ...artifactEnvironment,     // From system.environment artifact
  ANTHROPIC_API_KEY: key,
  WORKSPACE_PATH: workspacePath,
};
```

### MCP Server Configuration

```typescript
const mcpServers = {
  'filesystem': {
    transport: 'stdio',
    command: 'npx',
    args: ['@modelcontextprotocol/server-filesystem', workspacePath]
  },
  'github': {
    transport: 'stdio',
    command: 'npx',
    args: ['@modelcontextprotocol/server-github'],
    env: { GITHUB_TOKEN: '${GITHUB_TOKEN}' }
  }
};
```

---

## Mid-Turn Message Injection

A unique Miriad feature - messages can be pushed to agents during execution:

```typescript
interface MessageStream {
  push(message: UserMessage): void;
  close(): void;
}

// Usage
const stream = agent.createMessageStream();
stream.push({ role: 'user', content: 'New instruction mid-task' });
```

This enables:
- Human intervention during long tasks
- Agent-to-agent communication mid-execution
- Dynamic context updates

---

## Container Runtime

### Docker Configuration

Agents run in containers with:

```dockerfile
# Base tools
git, npm, uv, bunx, curl, jq, python3

# Claude integration
npm install -g @anthropic-ai/claude-code

# Runtime
Bun 1.3.6 (for Nuum engine)

# Networking
rathole (HTTP tunneling)

# User
Non-root 'agent' user
Workspace at /workspace
```

### Environment Injection

```bash
MIRIAD_CONFIG='{
  "spaceId": "...",
  "credentials": { "runtimeId": "...", "apiEndpoint": "..." },
  "workspace": "/workspace"
}'
ANTHROPIC_API_KEY=sk-...
GITHUB_TOKEN=ghp_...  # Optional
```

### Idle Timeout

Containers exit after 15 minutes of inactivity.

---

## Mapping to Agentive Starter Kit

### Current Agent Definition

```markdown
<!-- .claude/agents/feature-developer.md -->
---
name: feature-developer
description: Feature implementation specialist
model: claude-sonnet-4-20250514
tools:
  - Bash
  - Read
  - Write
  - Edit
  - ...
---

# Feature Developer

You are a feature implementation specialist...
```

### Enhanced Definition (Miriad-Inspired)

```markdown
<!-- .claude/agents/feature-developer.md -->
---
name: feature-developer
description: Feature implementation specialist for this project

# Engine config (Miriad-style)
engine: claude-code  # or future: custom-engine
model: claude-sonnet-4-20250514

# Tool access
tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep

# MCP servers (new)
mcp:
  - slug: filesystem
    transport: stdio
    command: npx
    args: ["@modelcontextprotocol/server-filesystem", "."]
  - slug: github
    transport: stdio
    command: npx
    args: ["@modelcontextprotocol/server-github"]

# Identity
nameTheme: developers  # For generating callsigns
singleton: false       # Allow multiple instances

# Discovery
featured: true         # Show in agent suggestions
---

# Feature Developer

You are a feature implementation specialist...
```

### Direct Mappings

| Miriad | Agentive Starter Kit |
|--------|---------------------|
| `system.agent` artifact | `.claude/agents/*.md` file |
| `engine` prop | `model` field (implicit claude-code engine) |
| `mcp[]` prop | `tools` list + future `mcp` config |
| `nameTheme` | `name` field |
| `featuredChannelStarter` | (not implemented) |
| Workspace isolation | Working directory per task |

### What We Can Adopt

1. **Structured MCP Configuration**
   ```yaml
   mcp:
     - slug: serena
       transport: stdio
       command: uvx
       args: ["serena"]
   ```

2. **Engine Abstraction** (future)
   ```yaml
   engine: claude-code  # Current default
   # Future: custom-engine, local-llm, etc.
   ```

3. **Agent Metadata**
   ```yaml
   singleton: true      # Only one instance allowed
   featured: true       # Show in suggestions
   nameTheme: engineers # For generating callsigns
   ```

4. **Environment Injection**
   ```yaml
   environment:
     GITHUB_TOKEN: ${GITHUB_TOKEN}
     PROJECT_ROOT: ${PWD}
   ```

### What Needs Adaptation

| Miriad Feature | Our Adaptation |
|----------------|----------------|
| Long-running engines | Ephemeral per-task execution |
| Subprocess management | Claude Code CLI invocation |
| Container isolation | Working directory isolation |
| Mid-turn injection | (Not applicable to ephemeral model) |
| Heartbeat/liveness | (Not needed for ephemeral) |

---

## Key Takeaways

1. **Agent as Artifact**: Defining agents as artifacts (files) with structured metadata is powerful and extensible.

2. **Engine Abstraction**: Separating agent definition from execution engine enables future flexibility.

3. **MCP Integration**: Their MCP configuration pattern is directly adoptable for structured tool access.

4. **Workspace Isolation**: Per-agent workspace paths provide security and organization.

5. **Dynamic Configuration**: System prompts and environment can be updated per-invocation.

---

## Recommendations

### Short-term

1. **Add `mcp` section** to agent definitions for structured MCP server config
2. **Add metadata fields** (`singleton`, `featured`, `nameTheme`)
3. **Standardize environment injection** via frontmatter

### Medium-term

1. **Create agent registry** listing available agents with capabilities
2. **Implement engine abstraction** for future non-Claude backends
3. **Add per-task workspace isolation** (already partially implemented via working directory)

### Long-term

1. **Consider mid-turn communication** if we move to longer-running agents
2. **Evaluate Nuum-style memory** for complex multi-task workflows
3. **Build agent spawning** for multi-agent orchestration

---

**Phase 4 Status**: ✅ Complete
**Recommendation**: Adopt structured MCP configuration and agent metadata; consider engine abstraction for future extensibility.
