# ASK-0013: Agent Session Initialization Pattern ADR

**Status**: Done
**Priority**: high
**Assigned To**: planner
**Estimated Effort**: 1-2 hours
**Created**: 2025-11-28
**Revised**: 2025-11-28 (scope clarification)

## Related Tasks

**Parent Task**: None (ADR Migration - Tier 2: Agent Coordination)
**Depends On**: None
**Blocks**: ASK-0020 (MCP Tool Addition Pattern)
**Related**: ADR-0002 (Serena MCP Integration - specific implementation)

## Overview

Create ADR-0006 documenting the **Agent Session Initialization Pattern** - the architectural pattern for ensuring agents properly activate tools and context at session start.

This is a **foundational pattern** that applies to:
- MCP tool activation (Serena, future tools)
- Project context initialization
- Any stateful setup agents need before working

**Why Essential**: Without explicit session initialization, agents have tools available but in the wrong context. This pattern prevents silent failures and ensures reliable tool operation.

## Scope Clarification

### What This ADR Covers (The Pattern)

| ADR-0006 Covers | Description |
|-----------------|-------------|
| The Problem | Tools globally available but project context missing |
| The Pattern | Launcher → Agent → Activation → Confirmation |
| Implementation | Agent markdown sections, launcher integration |
| Verification | How to confirm successful initialization |
| Failure Handling | What happens when activation fails |

### What ADR-0002 Covers (Serena-Specific)

| ADR-0002 Covers | Description |
|-----------------|-------------|
| Serena MCP setup | `claude mcp add` command |
| Project config | `.serena/project.yml` format |
| Language servers | Python, TypeScript, Swift LSP |
| Serena-specific activation | `mcp__serena__activate_project()` |

**Key Relationship**: ADR-0002 is a *specific implementation* of the pattern documented in ADR-0006.

## The Pattern

### Problem Statement

```
Agent starts in Claude Code CLI
    ↓
MCP tools available (globally configured via ~/.claude.json)
    ↓
BUT: Tools don't know which project/context to use
    ↓
Result: Tools fail silently or use wrong context
```

### Solution: Launcher-Initiated Activation

```
1. Launcher sends activation prompt as first message
    ↓
2. Agent's first action: Call activation function(s)
    ↓
3. Tool responds with confirmation
    ↓
4. Agent confirms to user, proceeds with task
```

### Pattern Components

**1. Agent Markdown Section**
```markdown
## Session Initialization

**IMPORTANT**: The launcher will send an initial activation request
as your first message. Immediately respond by:

1. Calling the required activation functions
2. Confirming activation in your response
3. Proceeding with the user's task

If activation fails, inform the user and suggest troubleshooting.
```

**2. Launcher Script Pattern**
```bash
claude --append-system-prompt "$(cat .claude/agents/$agent.md)" \
       -p "Please activate [tool] for [purpose] before we begin. Use: [activation_command]"
```

**3. Activation Confirmation**
```
Agent: "✅ [Tool] activated: [context]. Ready for [capability]."
```

## Requirements

### Functional Requirements

1. Document the session initialization pattern as an ADR
2. Explain why explicit activation is needed (vs auto-detection)
3. Define the launcher → agent → tool activation flow
4. Provide templates for agent markdown and launcher scripts
5. Document failure handling and fallback behavior

### Non-Functional Requirements

- ADR follows project template
- Pattern is tool-agnostic (not Serena-specific)
- Examples reference Serena as concrete implementation
- Clear distinction from ADR-0002

## Acceptance Criteria

### Must Have

- [ ] ADR-0006 created at `docs/decisions/adr/ADR-0006-agent-session-initialization.md`
- [ ] Follows project ADR template structure
- [ ] Documents the problem (tools without context)
- [ ] Explains the pattern (launcher-initiated activation)
- [ ] Provides agent markdown template (tool-agnostic)
- [ ] Provides launcher script template
- [ ] Documents alternatives considered
- [ ] Documents consequences (positive, negative, neutral)

### Should Have

- [ ] Failure handling guidance (what if activation fails)
- [ ] Verification approach (how to confirm success)
- [ ] Example with Serena (concrete implementation)
- [ ] Reference to ADR-0002 for Serena specifics

### Should NOT Have

- [ ] ❌ Serena-specific configuration details (that's ADR-0002)
- [ ] ❌ `.serena/project.yml` format (that's ADR-0002)
- [ ] ❌ MCP tool addition process (that's ASK-0020)

## Implementation Plan

### Step 1: Review Existing Materials (20 min)

1. Review ADR-0002 to understand current Serena documentation
2. Review agent files for current initialization patterns
3. Review launcher script(s)

### Step 2: Create ADR-0006 (45-60 min)

Create `docs/decisions/adr/ADR-0006-agent-session-initialization.md`:

**Context Section:**
- Problem: Tools available globally but lack project context
- Forces: MCP architecture, agent statelessness, CLI limitations
- Why auto-detection doesn't work

**Decision Section:**
- Adopt launcher-initiated activation pattern
- Agent markdown section template
- Launcher script pattern
- Confirmation protocol

**Consequences Section:**
- Positive: Reliable activation, explicit context
- Negative: Startup overhead, requires launcher discipline
- Neutral: Pattern must be followed consistently

**Alternatives Considered:**
- Auto-detection from working directory (rejected)
- Environment variable configuration (rejected)
- No explicit activation (rejected - current pain point)

### Step 3: Review and Finalize (20 min)

1. Verify no overlap with ADR-0002 Serena specifics
2. Ensure pattern is tool-agnostic
3. Check all acceptance criteria met

## Success Metrics

### Quantitative

- ADR-0006 created and follows template
- < 200 lines (pattern-focused, not tool-specific)
- All "Must Have" acceptance criteria met

### Qualitative

- Pattern applies to any future MCP tool
- Clear distinction from ADR-0002
- New agents can implement pattern without reading Serena docs

## Time Estimate

| Phase | Time |
|-------|------|
| Review existing materials | 20 min |
| Create ADR-0006 | 45-60 min |
| Review and finalize | 20 min |
| **Total** | **1-2 hours** |

## References

- **Related ADR**: `docs/decisions/adr/ADR-0002-serena-mcp-integration.md` (Serena implementation)
- **ADR Template**: `docs/decisions/adr/TEMPLATE-FOR-ADR-FILES.md`
- **Agent Files**: `.claude/agents/*.md` (current initialization sections)
- **Launcher Script**: `agents/launch` (if exists)
- **Future**: ASK-0020 (MCP Tool Addition Pattern)

## Notes

- This documents the **pattern**, not any specific tool
- ADR-0002 remains authoritative for Serena-specific details
- Serena is used as an example but pattern is generalizable
- Revised 2025-11-28 to clarify scope vs ADR-0002

---

**Template Version**: 1.0.0
**Created**: 2025-11-28
**Revised**: 2025-11-28
