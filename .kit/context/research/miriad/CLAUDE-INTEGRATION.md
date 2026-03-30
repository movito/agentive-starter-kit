# Claude Code Integration Analysis

**Date**: 2026-02-05
**Research Phase**: 5 (Claude Code Integration)
**Status**: Complete

---

## Executive Summary

Miriad integrates with Claude using the **@anthropic-ai/claude-agent-sdk**, Anthropic's official SDK for building AI agents. The SDK provides programmatic access to Claude Code's capabilities including file operations, command execution, and MCP tool integration.

**Key Insight**: The Claude Agent SDK is the officially supported way to build custom agents. Our current Claude Code CLI approach is simpler but the SDK offers more control for programmatic integration.

---

## Claude Agent SDK Overview

### What It Is

The Claude Agent SDK enables:
- Programmatic agent creation with Claude Code capabilities
- File reading, writing, and editing
- Shell command execution
- MCP server integration
- Session management with resume/fork
- Custom tool permissions

### Installation

```bash
npm install @anthropic-ai/claude-agent-sdk
```

**Requirements**: Node.js 18+

### Basic Usage

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Review and fix bugs in utils.py",
  options: {
    allowedTools: ["Read", "Edit", "Glob"],
    permissionMode: "acceptEdits"
  }
})) {
  if (message.type === "assistant") {
    // Handle Claude's responses
  } else if (message.type === "result") {
    // Task complete
  }
}
```

---

## How Miriad Uses the SDK

### Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Miriad Local Runtime                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────┐     ┌───────────────┐     ┌───────────┐ │
│   │ AgentManager │────►│ TymbalBridge  │────►│  Backend  │ │
│   └──────┬───────┘     └───────────────┘     │  Server   │ │
│          │                                    └───────────┘ │
│          │                                                   │
│          ▼                                                   │
│   ┌──────────────────┐                                      │
│   │ Claude Agent SDK │                                      │
│   │ (@anthropic-ai)  │                                      │
│   └──────────────────┘                                      │
│          │                                                   │
│          ▼                                                   │
│   ┌──────────────────┐                                      │
│   │   Claude API     │                                      │
│   └──────────────────┘                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Message Flow

1. **User Message** → AgentManager
2. AgentManager creates **MessageStream** for Claude SDK
3. Claude SDK processes via **query()** function
4. Responses flow through **TymbalBridge**
5. Bridge translates SDK messages → **Tymbal frames**
6. Frames broadcast to backend server via WebSocket

### TymbalBridge Translation

```
SDK Message Type        →    Tymbal Frame Type
─────────────────────────────────────────────
system (init)           →    (session setup)
assistant (text)        →    agent frame
assistant (tool_use)    →    tool_call frame
user (tool_result)      →    tool_result frame
result (success/error)  →    idle frame + cost frame
```

---

## Session Management

### Session ID Capture

```typescript
let sessionId: string;

for await (const message of query({ prompt, options })) {
  if (message.type === 'system' && message.subtype === 'init') {
    sessionId = message.session_id;
    // Save for later resumption
  }
}
```

### Session Resume

```typescript
const response = query({
  prompt: "Continue where we left off",
  options: {
    resume: sessionId,  // Continue previous session
    forkSession: false  // Don't create new branch (default)
  }
});
```

### Session Forking

| Behavior | `forkSession: false` | `forkSession: true` |
|----------|---------------------|---------------------|
| Session ID | Same as original | New ID generated |
| History | Appends to original | Creates branch |
| Original | Modified | Preserved |
| Use case | Linear continuation | Explore alternatives |

### Miriad's Session Handling

- **Check for `.claude` directory** in workspace
- If exists: `shouldContinue: true` (resume prior session)
- If not: Fresh session starts
- **SDK isolation mode**: No filesystem settings loaded (prevents key leakage)

---

## Tool Configuration

### Built-in Tools

| Tool | Purpose |
|------|---------|
| `Read` | Read any file |
| `Write` | Create new files |
| `Edit` | Make precise edits |
| `Bash` | Run terminal commands |
| `Glob` | Find files by pattern |
| `Grep` | Search file contents |
| `WebSearch` | Search the web |

### Tool Permission Levels

```typescript
// Specific tools only
allowedTools: ["Read", "Glob", "Grep"]  // Read-only

// Read + modify
allowedTools: ["Read", "Edit", "Glob"]  // Analysis + edits

// Full automation
allowedTools: ["Read", "Edit", "Bash", "Glob", "Grep"]
```

### Permission Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| `default` | Requires `canUseTool` callback | Custom approval flows |
| `acceptEdits` | Auto-approves file edits | Trusted development |
| `bypassPermissions` | Skips all prompts | CI/CD, automation |

---

## MCP Server Integration

### Configuration in SDK

```typescript
options: {
  mcpServers: {
    "github": {
      command: "npx",
      args: ["-y", "@modelcontextprotocol/server-github"],
      env: { GITHUB_TOKEN: process.env.GITHUB_TOKEN }
    },
    "filesystem": {
      command: "npx",
      args: ["@modelcontextprotocol/server-filesystem", "/path"]
    }
  },
  allowedTools: ["mcp__github__*", "mcp__filesystem__*"]
}
```

### Transport Types

| Transport | Use Case | Config |
|-----------|----------|--------|
| **stdio** | Local processes | `command`, `args`, `env` |
| **http** | Remote APIs | `type: "http"`, `url`, `headers` |
| **sse** | Streaming APIs | `type: "sse"`, `url`, `headers` |

### Tool Naming Convention

```
mcp__<server-name>__<tool-name>

Examples:
mcp__github__list_issues
mcp__filesystem__read_file
mcp__postgres__query
```

### MCP Tool Search (Large Tool Sets)

When tool definitions exceed 10% of context:
1. Tools marked with `defer_loading: true`
2. Claude uses search tool to discover relevant tools
3. Only needed tools loaded into context

Configure via environment:
```typescript
env: {
  ENABLE_TOOL_SEARCH: "auto"    // Default: 10% threshold
  ENABLE_TOOL_SEARCH: "auto:5"  // Custom: 5% threshold
  ENABLE_TOOL_SEARCH: "true"    // Always enabled
  ENABLE_TOOL_SEARCH: "false"   // Disabled
}
```

---

## Miriad-Specific Patterns

### Mid-Turn Message Injection

Miriad's unique feature - push messages during Claude processing:

```typescript
// Create stream for ongoing conversation
const stream = agent.createMessageStream();

// Initial message
stream.push({ role: 'user', content: 'Start implementing auth' });

// Mid-execution injection
setTimeout(() => {
  stream.push({ role: 'user', content: 'Also add rate limiting' });
}, 5000);
```

### Message Formatting

Messages include sender attribution:
```
--- @{sender} says:
{content}
```

### Cost Tracking

SDK returns usage metrics:
```typescript
interface CostFrame {
  inputTokens: number;
  outputTokens: number;
  cacheReadTokens: number;
  cacheWriteTokens: number;
  duration: number;
}
```

### Engine Selection

Miriad supports two engines:

| Engine | Use | Characteristics |
|--------|-----|-----------------|
| `claude-sdk` | Default | In-process, native Claude Code tools |
| `nuum` | Alternative | Subprocess (Bun), 3-tier memory |

---

## Comparison: SDK vs CLI

### Claude Agent SDK

```typescript
// Programmatic, full control
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "...",
  options: {
    allowedTools: [...],
    mcpServers: {...},
    systemPrompt: "..."
  }
})) {
  // Handle streaming messages
}
```

**Pros**:
- Full streaming control
- Session management (resume/fork)
- Programmatic tool permissions
- MCP server configuration
- Cost tracking
- Multi-turn conversations

**Cons**:
- Requires Node.js runtime
- More complex setup
- Need to handle message types

### Claude Code CLI

```bash
# Simple invocation
claude "Review and fix bugs" --allowedTools Read,Edit,Glob
```

**Pros**:
- Simple, one-line invocation
- No code required
- Built-in terminal UI
- Immediate use

**Cons**:
- Less programmatic control
- Session handling via filesystem
- Tool permissions via flags/config

---

## Mapping to Agentive Starter Kit

### Current Approach (CLI-based)

```bash
# Agent invoked via Claude Code CLI
# Tools controlled by .claude/agents/*.md definitions
# Session via working directory
```

### SDK Approach (Alternative)

```typescript
// Could wrap agents in SDK calls
import { query } from "@anthropic-ai/claude-agent-sdk";

async function runAgent(agentConfig: AgentDefinition, task: string) {
  const options = {
    systemPrompt: agentConfig.systemPrompt,
    allowedTools: agentConfig.tools,
    mcpServers: agentConfig.mcp,
    permissionMode: "acceptEdits"
  };

  for await (const message of query({ prompt: task, options })) {
    // Handle streaming, log to channel, etc.
  }
}
```

### Hybrid Approach (Recommended)

Keep CLI for simplicity, but learn from SDK patterns:

1. **Session Management**: Add session IDs to handoff files
2. **Tool Configuration**: Structured MCP config in agent definitions
3. **Cost Tracking**: Log token usage from tool results
4. **Message Streaming**: File-based equivalent for CLI output

---

## Adoption Recommendations

### Immediate (No Code Changes)

1. **Document SDK option** for advanced users
2. **Learn permission patterns** (acceptEdits, bypassPermissions)
3. **Understand session model** for future file-based sessions

### Short-term

1. **Add MCP config format** to agent definitions:
   ```yaml
   mcp:
     - slug: serena
       command: uvx
       args: ["serena"]
   ```

2. **Track costs** by logging tool result metadata

3. **Session IDs** in handoff files for continuity tracking

### Medium-term

1. **Evaluate SDK adoption** for orchestration layer
2. **Mid-turn communication** if moving to longer sessions
3. **Tool search** for large MCP tool sets

### Long-term

1. **Custom orchestration** using SDK for multi-agent coordination
2. **Streaming to file** for real-time CLI updates
3. **Engine abstraction** to support SDK alongside CLI

---

## Key Takeaways

1. **Official SDK**: `@anthropic-ai/claude-agent-sdk` is the supported way to build programmatic agents

2. **Session Management**: SDK supports resume/fork - we could adapt for file-based session continuity

3. **MCP Integration**: SDK has first-class MCP support - adopt their config format

4. **Permission Modes**: Three levels (default/acceptEdits/bypassPermissions) - useful for automation

5. **Miriad's TymbalBridge**: Translates SDK messages to Tymbal frames - we could do similar for file-based logging

6. **Mid-Turn Injection**: Unique Miriad feature - not applicable to our ephemeral model but interesting for future

---

## Sources

- [Claude Agent SDK Quickstart](https://platform.claude.com/docs/en/agent-sdk/quickstart)
- [Sessions Documentation](https://platform.claude.com/docs/en/agent-sdk/sessions)
- [MCP Integration Guide](https://platform.claude.com/docs/en/agent-sdk/mcp)
- [GitHub: anthropics/claude-agent-sdk-typescript](https://github.com/anthropics/claude-agent-sdk-typescript)
- [npm: @anthropic-ai/claude-agent-sdk](https://www.npmjs.com/package/@anthropic-ai/claude-agent-sdk)

---

**Phase 5 Status**: ✅ Complete
**Recommendation**: Continue using CLI for simplicity; adopt SDK patterns for MCP config, session tracking, and permission models. Consider SDK for future orchestration needs.
