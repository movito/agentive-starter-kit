# KIT-ADR-0006: Agent Session Initialization Pattern

**Status**: Accepted

**Date**: 2025-11-28

**Deciders**: planner, User

## Context

### Problem Statement

AI agents need to activate project-specific tools and context at session start. Without explicit initialization, tools are available globally but lack the project context needed for correct operation, leading to silent failures or incorrect behavior.

```
Agent starts in Claude Code CLI
    ↓
MCP tools available (globally configured via ~/.claude.json)
    ↓
BUT: Tools don't know which project/context to use
    ↓
Result: Tools fail silently or use wrong context
```

### Forces at Play

**Technical Requirements:**
- MCP tools are configured at user level (globally available)
- Each project has unique configuration requirements
- Agents are stateless - no memory of previous sessions
- CLI environment lacks automatic project detection

**Constraints:**
- Cannot modify MCP architecture (it's external)
- Agents cannot auto-detect project from environment alone
- Launcher scripts must work across different agent types
- Pattern must be tool-agnostic (work for any MCP tool)

**Assumptions:**
- Agents are launched via CLI or automation scripts
- Each project defines its own tool configurations
- Agents can execute tool calls as their first action
- Tool activation produces a confirmable response

## Decision

We will adopt **launcher-initiated activation** as the standard pattern for agent session initialization.

### Core Principles

1. **Explicit over implicit**: Always explicitly activate tools rather than relying on auto-detection
2. **Fail-fast with clarity**: If activation fails, inform user immediately with actionable guidance
3. **Tool-agnostic pattern**: Same initialization flow works for any MCP tool
4. **Launcher responsibility**: The launcher (not the agent) initiates the activation request

### Implementation Details

**The Activation Flow:**

```
1. Launcher sends activation prompt as first message
    ↓
2. Agent's first action: Call activation function(s)
    ↓
3. Tool responds with success/failure
    ↓
4. Agent confirms to user OR handles failure
    ↓
5. Agent proceeds with task (if successful)
```

**Component 1: Agent Markdown Section**

Every agent file should include a session initialization section:

```markdown
## Session Initialization

**IMPORTANT**: The launcher will send an initial activation request
as your first message. When you see a request to activate [Tool],
immediately respond by calling:

```
[tool_activation_function]("[project-name]")
```

This configures [tool capabilities]. Confirm activation in your
response: "✅ [Tool] activated: [context]. Ready for [capability]."

If activation fails:
1. Check if the tool is properly installed
2. Verify project configuration exists
3. Inform user with specific error and remediation steps
```

**Component 2: Launcher Script Pattern**

```bash
#!/bin/bash
# Generic launcher pattern

AGENT="$1"
PROJECT="your-project-name"
TOOL="tool-name"
ACTIVATION_CMD="mcp__tool__activate_project(\"$PROJECT\")"

claude --append-system-prompt "$(cat .claude/agents/$AGENT.md)" \
       -p "Please activate $TOOL for $PROJECT before we begin. Use: $ACTIVATION_CMD"
```

**Component 3: Activation Confirmation Protocol**

Successful activation:
```
Agent: "✅ [Tool] activated: [context details]. Ready for [capabilities]."
```

Failed activation:
```
Agent: "⚠️ [Tool] activation failed: [error].
Troubleshooting:
1. [Check 1]
2. [Check 2]
Please resolve and retry."
```

### Error Handling

**Activation Failure Scenarios:**

| Scenario | Detection | Response |
|----------|-----------|----------|
| Tool not installed | MCP function not found | Inform user to run setup script |
| Project not configured | Activation returns error | Guide user to create config file |
| Invalid configuration | Tool reports parse error | Show config requirements |
| Timeout | No response within limit | Retry once, then inform user |

**Graceful Degradation:**

If activation fails, agents should:
1. **NOT proceed silently** - always inform the user
2. **Offer alternatives** - suggest fallback tools if available
3. **Provide remediation** - specific steps to fix the issue
4. **Continue if non-critical** - some tools may be optional for certain tasks

### Verification Approach

**How to confirm successful initialization:**

1. **Tool response check**: Activation function returns success message
2. **Capability test**: Optionally, run a simple tool command to verify
3. **Context confirmation**: Tool reports correct project/context is active

**Example verification in agent markdown:**

```markdown
After activation, verify by running a simple command:
```
mcp__serena__get_current_config()  # Should show correct project
```
```

## Consequences

### Positive

- ✅ **Reliable activation**: Explicit initialization ensures correct context
- ✅ **Clear failure modes**: Users know immediately if something is wrong
- ✅ **Tool-agnostic**: Same pattern works for any MCP tool
- ✅ **Self-documenting**: Agent markdown explains the activation requirement
- ✅ **Automation-friendly**: Launcher scripts can be standardized

### Negative

- ⚠️ **Startup overhead**: Extra round-trip for activation before work begins
- ⚠️ **Launcher discipline required**: Must include activation prompt in all launches
- ⚠️ **Agent file maintenance**: All agents need initialization section updated

### Neutral

- 📊 **Pattern consistency**: All agents follow same initialization approach
- 📊 **Documentation coupling**: Agent markdown tied to tool activation requirements

## Alternatives Considered

### Alternative 1: Auto-detection from Working Directory

**Description**: Tools auto-detect project from current working directory

**Rejected because**:
- ❌ Working directory isn't always reliable (agents launched from various locations)
- ❌ Some tools require explicit project registration
- ❌ No way to ensure correct configuration is loaded
- ❌ Silent failures when detection fails

### Alternative 2: Environment Variable Configuration

**Description**: Set project context via environment variables before launch

**Rejected because**:
- ❌ Environment variables not reliably passed to MCP tools
- ❌ Harder to verify correct setup
- ❌ Different tools may need different env vars
- ❌ No confirmation of successful activation

### Alternative 3: No Explicit Activation

**Description**: Assume tools work without activation, handle errors ad-hoc

**Rejected because**:
- ❌ Current pain point - agents have tools but wrong context
- ❌ Silent failures lead to incorrect results
- ❌ Inconsistent behavior across sessions
- ❌ Users don't know why things aren't working

### Alternative 4: Tool-side Auto-activation

**Description**: Tools detect agent launch and auto-activate appropriate project

**Rejected because**:
- ❌ Requires modifying MCP tool implementations
- ❌ Tools can't reliably detect which project is intended
- ❌ Coupling between tool and project detection logic
- ❌ Not all tools can support this pattern

## Real-World Results

**Before this pattern (ad-hoc activation):**
- Agents had tools available but in wrong context
- Silent failures: tools returned errors or incorrect data
- Users confused why semantic navigation wasn't working
- Inconsistent behavior across different agent sessions

**After this pattern:**
- Agents reliably activate correct project context
- Clear feedback when activation fails
- Consistent behavior across all agent sessions
- Users understand the activation requirement

**Key Discovery:**
- Agents didn't auto-activate despite having tools available
- Required explicit "Session Initialization" section in agent definitions
- Activation must be positioned as startup protocol, not optional guidance

## Related Decisions

- KIT-ADR-0002: Serena MCP Integration (specific implementation of this pattern for Serena)

## References

- Agent files: `.claude/agents/*.md` (current implementation)
- Launcher scripts: `agents/launch` (if exists)
- Claude Code MCP Documentation: https://docs.claude.com/en/docs/claude-code

## Revision History

- 2025-11-28: Initial decision (Accepted)
  - Documented launcher-initiated activation pattern
  - Defined error handling and verification approaches
  - Established templates for agents and launchers

---

**Template Version**: 1.1.0
**Last Updated**: 2025-11-28
**Project**: agentive-starter-kit
