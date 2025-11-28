# ADR-0003: Custom Linear Sync over Linear MCP

**Status**: Accepted

**Date**: 2025-11-28

**Deciders**: planner, coordinator

## Context

### Problem Statement

The project has a custom Linear sync implementation (`scripts/sync_tasks_to_linear.py`) that syncs markdown task files to Linear issues. Linear also offers an official MCP (Model Context Protocol) server with 21 tools for interacting with Linear. We needed to decide whether to:

1. Keep and improve the custom sync implementation
2. Replace it with Linear's official MCP
3. Use a hybrid approach combining both

### Forces at Play

**Technical Requirements:**
- Tasks must be version-controlled in git
- Folder-based status organization (`1-backlog/` through `7-blocked/`)
- Automated sync on CI/CD (GitHub Actions)
- GitHub backlinks in Linear issues
- Offline editing capability

**Constraints:**
- Limited development resources for maintenance
- Need for consistency with existing workflow
- Agent-based development relies on file-based task specs

**Assumptions:**
- Git repository remains the source of truth for task definitions
- Agents will continue to work primarily with markdown task files
- Linear is used for team visibility, not as primary authoring interface

## Decision

We will **keep the custom Linear sync implementation** as the primary mechanism for syncing tasks to Linear, while documenting Linear MCP as a potential supplementary tool for real-time queries.

### Core Principles

1. **Git as Source of Truth**: Task definitions live in the repository, version-controlled and reviewable
2. **Folder-Based Workflow**: Status is determined by folder location, enabling intuitive file organization
3. **Batch Sync on CI/CD**: All tasks sync atomically on push, not individual operations
4. **Agent-Friendly**: Markdown task files are the interface agents use to understand and execute work

### Implementation Details

**Current sync architecture:**
- `scripts/sync_tasks_to_linear.py` (~500 lines) - Main sync orchestrator
- `scripts/linear_sync_utils.py` (~391 lines) - Status mapping utilities
- `.github/workflows/sync-to-linear.yml` - GitHub Actions automation

**Key capabilities:**
- One-way sync (files → Linear issues)
- 3-level status priority (Status field → Folder → Default)
- Legacy status migration (auto-updates files)
- GitHub backlinks in issue descriptions
- Comprehensive test suite (50+ tests)

**CLI usage:**
```bash
./project linearsync
```

## Consequences

### Positive

- **Version control**: Task history preserved in git, enabling blame, diff, and rollback
- **Offline-first**: Tasks can be created/edited without Linear connectivity
- **CI/CD integration**: Sync happens automatically on push to main/develop
- **Custom metadata**: Supports fields Linear doesn't (effort estimates, dependencies, agent assignments)
- **Folder-based UX**: Moving files between folders changes status intuitively
- **GitHub integration**: Issues link back to source files in repository

### Negative

- **Maintenance burden**: Custom code requires ongoing maintenance
- **One-way only**: Changes in Linear don't propagate back to files
- **No real-time queries**: Can't ask "show me all blocked issues" without external tooling
- **Sync latency**: Changes only appear in Linear after git push + CI run

### Neutral

- **Linear MCP remains available**: Can be added later for supplementary use cases
- **Daemon capability planned**: Future `./project daemon` could add continuous sync

## Alternatives Considered

### Alternative 1: Replace with Linear MCP

**Description**: Remove custom sync entirely and use Linear's official MCP server as the only integration. Tasks would be created/managed directly in Linear.

**Rejected because**:
- Linear becomes source of truth, losing git version control
- No folder-based status workflow
- No batch sync capability (individual operations only)
- No GitHub backlinks to source files
- Breaks agent workflow that depends on markdown task files
- Requires connectivity for all operations

### Alternative 2: Hybrid Approach (Recommended for Future)

**Description**: Keep custom sync for file→Linear direction, add Linear MCP for real-time queries and supplementary operations.

**Not implemented now because**:
- Current sync meets all immediate needs
- MCP integration adds complexity without urgent benefit
- Can be revisited when real-time query needs emerge

**Future use cases for Linear MCP:**
- Real-time queries: "Show me all my high-priority issues"
- Comment management: Adding comments without file editing
- Ad-hoc issue updates: Quick status changes during discussions
- Team coordination: "What's blocking the frontend team?"

### Alternative 3: Bidirectional Sync

**Description**: Extend custom sync to also pull changes from Linear back to files.

**Deferred because**:
- Significant complexity (conflict resolution, merge strategies)
- Risk of overwriting local changes
- Current workflow doesn't require it (Linear is view-only)
- Could be added later if team starts editing in Linear

## Real-World Results

**Current implementation status:**
- Sync script: Production-ready
- Test suite: 50+ tests (TDD, awaiting full implementation)
- GitHub Actions: Configured and operational
- ASK-0005 task: Active improvement work ongoing

**Observed benefits:**
- Tasks visible in Linear for team coordination
- No manual issue creation required
- Status automatically derived from folder structure

## Related Decisions

- ADR-0002: Serena MCP Integration (demonstrates MCP adoption for code navigation)

## References

- Linear MCP documentation: https://linear.app/docs/mcp
- Linear MCP tools list: https://www.remote-mcp.com/servers/linear
- MCP Protocol specification: https://modelcontextprotocol.io/specification/2025-06-18
- Current sync implementation: `scripts/sync_tasks_to_linear.py`
- Task management documentation: `docs/LINEAR-SYNC-BEHAVIOR.md`
- Active improvement task: `delegation/tasks/2-todo/ASK-0005-linear-sync-infrastructure.md`

## Revision History

- 2025-11-28: Initial decision (Accepted)

---

**Template Version**: 1.1.0
**Project**: agentive-starter-kit
