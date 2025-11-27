# ADR-0002: Serena MCP Integration for Semantic Code Navigation

**Status**: Accepted

**Date**: 2025-11-27

**Deciders**: rem (coordinator), User

## Context

### Problem Statement

AI agents need efficient code navigation to understand and modify codebases. Traditional approaches (Grep, Read, Glob) are token-expensive and lack semantic understanding. We need a solution that provides:
- Symbol-aware code navigation
- Reference finding across the codebase
- Efficient token usage (70-98% savings)

### Forces at Play

**Technical Requirements:**
- Support for Python, TypeScript, Swift, and other languages
- Integration with Claude Code CLI agents
- Works across multiple projects without reconfiguration

**Constraints:**
- Must work with Claude Code's MCP (Model Context Protocol) system
- Agents are launched per-project but MCP config is shared
- Each project has its own `.serena/project.yml` configuration

**Assumptions:**
- Users have uvx or pipx installed for Python tool execution
- Projects using Serena will define language servers in project.yml
- Agents need explicit project activation before using Serena tools

## Decision

We will integrate Serena MCP with **user-level scope** and **launcher-initiated activation**.

### Core Principles

1. **User-level MCP scope**: Serena is configured once, available to all projects
2. **Project-specific activation**: Each project has its own `.serena/project.yml`
3. **Agent-initiated activation**: Agents call `mcp__serena__activate_project()` on startup

### Implementation Details

**MCP Configuration (user-level):**

```bash
# Setup script uses --scope user for global availability
claude mcp add --scope user serena -- uvx --from "git+https://github.com/oraios/serena" serena-mcp-server
```

**Project Configuration (`.serena/project.yml`):**

```yaml
project_name: "my-project"
languages:
  - python
  - typescript
encoding: "utf-8"
ignore_all_files_in_gitignore: true
```

**Agent Activation (in agent markdown files):**

```markdown
## Serena Activation (Launcher-Initiated)

When you see a request to activate Serena, immediately respond by calling:

```
mcp__serena__activate_project("my-project")
```
```

**Onboarding Process:**

During onboarding, the `"your-project"` placeholder in agent files is replaced with the actual project name:

```bash
for agent_file in .claude/agents/*.md; do
  sed -i '' "s/activate_project(\"your-project\")/activate_project(\"actual-project-name\")/" "$agent_file"
done
```

## Consequences

### Positive

- ✅ **Token efficiency**: 70-98% reduction in tokens for code navigation
- ✅ **Semantic understanding**: Find references, definitions, symbols accurately
- ✅ **Global availability**: One setup, works across all projects
- ✅ **Language flexibility**: Supports multiple LSP-backed languages

### Negative

- ⚠️ **Startup overhead**: Agents must explicitly activate project
- ⚠️ **Fallback to "desktop-app"**: If activation fails, Serena uses default context
- ⚠️ **Browser popup**: Setup may open browser window (harmless, user should close)

### Neutral

- 📊 **Per-project config**: Each project needs `.serena/project.yml`
- 📊 **LSP dependency**: Requires language servers for each language

## Alternatives Considered

### Alternative 1: Local-scoped MCP Configuration

**Description**: Configure Serena per-project using default `--scope local`

**Rejected because**:
- ❌ Serena unavailable when launching agents from different projects
- ❌ Requires running setup in every project individually
- ❌ Causes agents to fall back to "desktop-app" context

### Alternative 2: No Explicit Activation

**Description**: Have Serena auto-detect project from working directory

**Rejected because**:
- ❌ Serena needs explicit project registration in `~/.serena/serena_config.yml`
- ❌ Working directory isn't always reliable (agents launched from various locations)
- ❌ No way to ensure correct LSP servers are started

### Alternative 3: Claude Desktop Integration Only

**Description**: Use Serena only through Claude Desktop app

**Rejected because**:
- ❌ Agents run via Claude Code CLI, not Desktop
- ❌ Different MCP configuration paths
- ❌ Doesn't support agentive workflow

## Real-World Results

**Before this decision (thematic-cuts project):**
- Agents using Grep/Read/Glob for code navigation
- High token usage for understanding codebase
- No reference finding capability

**After this decision:**
- 70-98% token savings on code navigation tasks
- Accurate symbol and reference finding
- Works consistently across coordinator, feature-developer, test-runner agents

**Key Discovery (from thematic-cuts ADR-0041):**
- Agents didn't auto-activate Serena despite available tools
- Required explicit "Session Initialization" pattern in agent definitions
- Activation must be positioned as startup protocol, not optional guidance

## Related Decisions

- ADR-0001: System Prompt Size Considerations (token efficiency)
- thematic-cuts ADR-0040: Serena Adoption Decision
- thematic-cuts ADR-0041: Mandatory Session Initialization Pattern

## References

- [Serena Documentation](https://oraios.github.io/serena/)
- [Serena GitHub Repository](https://github.com/oraios/serena)
- [Claude Code MCP Documentation](https://docs.claude.com/en/docs/claude-code)
- Setup script: `.serena/setup-serena.sh`
- Project template: `.serena/project.yml.template`

## Revision History

- 2025-11-27: Initial decision (Accepted)
  - User-level MCP scope for global availability
  - Agent file placeholder replacement during onboarding
  - Documented activation pattern from thematic-cuts learnings

---

**Template Version**: 1.1.0
**Last Updated**: 2025-11-27
**Project**: agentive-starter-kit
