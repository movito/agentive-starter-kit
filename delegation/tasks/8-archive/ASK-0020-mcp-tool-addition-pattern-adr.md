# ASK-0020: MCP Tool Addition Pattern ADR

**Status**: Done
**Priority**: medium
**Assigned To**: planner
**Estimated Effort**: 1-2 hours
**Created**: 2025-11-28

## Related Tasks

**Parent Task**: None
**Depends On**: ASK-0013 (Agent Session Initialization Pattern)
**Blocks**: None
**Related**: KIT-ADR-0002 (Serena MCP Integration)

## Overview

Create an ADR documenting the generalized pattern for adding new MCP tools to the agentive-starter-kit. This provides a repeatable process for integrating future MCP servers (database, API, file system, etc.).

**Why Valuable**: As the MCP ecosystem grows, we'll want to add more tools. Having a documented pattern ensures consistency and reduces integration time.

## Key Concepts to Document

### MCP Tool Integration Checklist

1. **MCP Server Setup**
   - Global vs local scope decision
   - Installation command pattern
   - Configuration file locations

2. **Project Configuration**
   - Per-project config file (like `.serena/project.yml`)
   - Environment variables
   - Secrets handling

3. **Agent Integration**
   - Session initialization pattern (see ADR from ASK-0013)
   - Agent markdown sections
   - Launcher script updates

4. **Documentation**
   - Usage guide
   - Troubleshooting
   - Examples

### Example Tools (Future)

| Tool | Purpose | Activation Pattern |
|------|---------|-------------------|
| Database MCP | SQL queries | `mcp__db__connect("connection-string")` |
| API MCP | External APIs | `mcp__api__configure("api-name")` |
| File System MCP | Extended file ops | `mcp__fs__set_root("/path")` |

## Acceptance Criteria

### Must Have

- [ ] ADR created following project template
- [ ] Documents MCP tool integration checklist
- [ ] References Agent Session Initialization pattern (ASK-0013)
- [ ] Provides decision framework for scope (global vs local)

### Should Have

- [ ] Example integration for hypothetical tool
- [ ] Security considerations for MCP tools
- [ ] Testing approach for new MCP integrations

## Notes

- This is a **future** task - create when actually adding a second MCP tool
- May be YAGNI if Serena remains the only MCP tool
- Depends on ASK-0013 for the session initialization pattern

---

**Template Version**: 1.0.0
**Created**: 2025-11-28
