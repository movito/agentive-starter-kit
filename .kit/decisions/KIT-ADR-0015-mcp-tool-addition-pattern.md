# KIT-ADR-0015: MCP Tool Addition Pattern

**Status**: Accepted

**Date**: 2025-11-29

**Deciders**: planner, User

## Context

### Problem Statement

As the MCP (Model Context Protocol) ecosystem grows, projects may need to integrate additional MCP tools beyond Serena. Each integration requires consistent configuration, activation patterns, and documentation. Without a standardized approach:
- Integrations become ad-hoc and inconsistent
- Agent files diverge in structure and patterns
- Troubleshooting becomes harder across different tools
- Onboarding friction increases

### Forces at Play

**Technical Requirements:**
- MCP tools are external to the project (third-party servers)
- Claude Code supports both global (`--scope user`) and local (`--scope local`) MCP configurations
- Tools require project-specific configuration for context
- Agents need to activate tools at session start

**Constraints:**
- MCP configuration is managed through `claude mcp` CLI
- Each tool has unique configuration requirements
- Secrets and credentials must be handled securely
- Agents are stateless across sessions

**Assumptions:**
- Projects may integrate multiple MCP tools over time
- Each tool provides specific capabilities (code navigation, database, APIs, etc.)
- Consistent patterns reduce cognitive load for developers
- Documentation enables self-service troubleshooting

## Decision

We will adopt a **standardized MCP Tool Addition Pattern** with four phases: Setup, Configuration, Integration, and Documentation.

### Core Principles

1. **Prefer user-level scope**: Install MCP tools globally for availability across projects
2. **Project-specific config**: Each project defines its own tool configuration files
3. **Launcher-initiated activation**: Agents activate tools via explicit calls at session start
4. **Complete documentation**: Every integration includes setup, usage, and troubleshooting guides

### The Four-Phase Pattern

#### Phase 1: MCP Server Setup

**Scope Decision Matrix:**

| Criterion | User Scope | Local Scope |
|-----------|------------|-------------|
| Multiple projects use tool | ✅ Preferred | |
| Single project only | | ✅ Preferred |
| Shared credentials | ✅ Preferred | |
| Project-specific credentials | | ✅ Preferred |
| Team standardization | ✅ Preferred | |

**Installation Command Pattern:**

```bash
# User scope (recommended for multi-project tools)
claude mcp add --scope user <tool-name> -- <runner> <package> <args>

# Local scope (for project-specific tools)
claude mcp add --scope local <tool-name> -- <runner> <package> <args>
```

**Examples:**

```bash
# Serena (code navigation) - user scope
claude mcp add --scope user serena -- uvx --from "git+https://github.com/oraios/serena" serena-mcp-server

# Hypothetical database tool - user scope
claude mcp add --scope user db-client -- npx @mcp/database-client

# Hypothetical API gateway - local scope (project-specific)
claude mcp add --scope local api-gateway -- python -m api_gateway_mcp
```

#### Phase 2: Project Configuration

**Configuration File Pattern:**

Each tool should have a project-specific config in a dedicated folder:

```
.<tool-name>/
├── project.yml          # Main configuration
├── project.yml.template # Template for onboarding
└── setup-<tool>.sh      # Optional setup script
```

**Configuration File Structure:**

```yaml
# .<tool-name>/project.yml
project_name: "your-project-name"
# Tool-specific settings...
```

**Environment Variables Pattern:**

```bash
# .env.template
# <TOOL-NAME> Configuration
<TOOL>_API_KEY=           # Required: API key for <tool>
<TOOL>_ENDPOINT=          # Optional: Custom endpoint (default: https://api.example.com)
<TOOL>_DEBUG=false        # Optional: Enable debug logging
```

**Secrets Handling:**

| Secret Type | Storage | Access Method |
|-------------|---------|---------------|
| API keys | `.env` (gitignored) | Environment variable |
| OAuth tokens | OS keychain | Tool-specific retrieval |
| Certificates | `~/.config/<tool>/` | File path in config |

#### Phase 3: Agent Integration

**Agent Markdown Section Template:**

Add this section to each agent that uses the tool:

```markdown
## <Tool Name> Activation (Launcher-Initiated)

**IMPORTANT**: The launcher will send an initial activation request
as your first message. When you see a request to activate <Tool>,
immediately respond by calling:

```
mcp__<tool>__<activation_function>("<project-name>")
```

This configures <tool capabilities>. Confirm activation in your
response: "✅ <Tool> activated: <context>. Ready for <capability>."

After activation, use <tool> functions for <key benefits>.
If activation was skipped or failed, activate before any
<tool-specific> operations.
```

**Activation Function Naming Convention:**

| Tool Type | Activation Function Example |
|-----------|----------------------------|
| Code navigation | `mcp__serena__activate_project("name")` |
| Database | `mcp__db__connect("connection-name")` |
| API gateway | `mcp__api__configure("api-profile")` |
| File system | `mcp__fs__set_context("/path")` |

**Onboarding Placeholder Replacement:**

During project onboarding, replace placeholders in agent files:

```bash
# In onboarding script
for agent_file in .claude/agents/*.md; do
  sed -i '' 's/<your-project>/actual-project-name/g' "$agent_file"
done
```

#### Phase 4: Documentation

**Required Documentation Files:**

1. **Setup Guide** (in `.<tool>/README.md` or `docs/mcp/<tool>.md`):
   ```markdown
   # <Tool> Integration

   ## Prerequisites
   - [List prerequisites]

   ## Installation
   [Step-by-step installation]

   ## Configuration
   [Project config setup]

   ## Verification
   [How to verify installation]
   ```

2. **Troubleshooting Section** (in ADR or separate doc):
   - Common error messages and solutions
   - Debug logging instructions
   - Contact/support information

3. **Agent Examples** (in agent markdown):
   - When to use the tool
   - Key functions and their purposes
   - Expected responses

### Checklist for Adding New MCP Tool

```markdown
## MCP Tool Addition Checklist: <Tool Name>

### Phase 1: Setup
- [ ] Determine scope (user vs local)
- [ ] Install MCP server via `claude mcp add`
- [ ] Verify installation with `claude mcp list`

### Phase 2: Configuration
- [ ] Create `.<tool>/` directory
- [ ] Create `project.yml` with project settings
- [ ] Create `project.yml.template` for onboarding
- [ ] Add environment variables to `.env.template`
- [ ] Document secrets handling approach

### Phase 3: Integration
- [ ] Add activation section to relevant agent files
- [ ] Update launcher scripts (if applicable)
- [ ] Add placeholder replacement to onboarding script
- [ ] Test activation with each agent type

### Phase 4: Documentation
- [ ] Create setup/usage guide
- [ ] Document troubleshooting scenarios
- [ ] Add examples to agent files
- [ ] Update project README if needed
- [ ] Create ADR for this integration

### Verification
- [ ] Tool activates successfully in new session
- [ ] Tool works correctly after activation
- [ ] Errors are handled gracefully
- [ ] Documentation is complete and accurate
```

## Consequences

### Positive

- ✅ **Consistency**: All MCP tools follow the same integration pattern
- ✅ **Discoverability**: Standard locations for configuration and docs
- ✅ **Maintainability**: Easier to update or replace tools
- ✅ **Onboarding**: New tools integrate into existing workflow
- ✅ **Troubleshooting**: Predictable error handling and documentation

### Negative

- ⚠️ **Overhead**: Each tool requires full four-phase process
- ⚠️ **Rigidity**: Pattern may not fit all tools perfectly
- ⚠️ **Maintenance**: Multiple agent files need updating for each tool

### Neutral

- 📊 **Learning curve**: Pattern requires upfront understanding
- 📊 **Tool diversity**: Different tools may have unique requirements

## Example: Hypothetical Database MCP Tool

**Phase 1: Setup**
```bash
claude mcp add --scope user db-client -- npx @mcp/postgres-client
```

**Phase 2: Configuration**
```yaml
# .db-client/project.yml
project_name: "my-project"
default_connection: "local-dev"
connections:
  local-dev:
    host: localhost
    port: 5432
    database: myapp_dev
  production:
    host: "${DB_PROD_HOST}"
    port: 5432
    database: myapp_prod
```

**Phase 3: Agent Section**
```markdown
## Database Activation (Launcher-Initiated)

**IMPORTANT**: The launcher will send an initial activation request
as your first message. When you see a request to activate Database,
immediately respond by calling:

```
mcp__db__connect("local-dev")
```

This connects to the configured database. Confirm activation in your
response: "✅ Database activated: local-dev. Ready for queries."
```

**Phase 4: Verification**
```bash
# After activation, verify with:
mcp__db__run_query("SELECT 1")  # Should return 1
```

## Security Considerations

### Credential Management

1. **Never commit secrets**: Use `.env` files (gitignored) or environment variables
2. **Use OS keychain**: For long-lived credentials
3. **Rotate regularly**: Document rotation procedures
4. **Least privilege**: Tools should request minimal permissions

### Network Security

1. **TLS required**: All connections should use HTTPS/TLS
2. **Firewall rules**: Document required network access
3. **Proxy support**: Document proxy configuration if applicable

### Access Control

1. **Tool-level permissions**: Some tools support read-only modes
2. **Project isolation**: User-scope tools should still respect project boundaries
3. **Audit logging**: Enable if tool supports it

## Testing Approach for New Integrations

### Manual Verification

1. **Installation test**: `claude mcp list` shows tool
2. **Activation test**: Agent successfully activates tool
3. **Function test**: Basic tool functions work correctly
4. **Error test**: Intentional errors produce clear messages

### Automated Verification (if applicable)

```python
# tests/test_mcp_integration.py
def test_tool_activates():
    """Tool should activate successfully."""
    # Invoke agent with activation prompt
    # Assert activation confirmation received

def test_tool_function_works():
    """Basic function should work after activation."""
    # Activate tool
    # Run basic function
    # Assert expected result

def test_tool_error_handling():
    """Errors should produce clear messages."""
    # Attempt invalid operation
    # Assert error message is actionable
```

## Related Decisions

- KIT-ADR-0002: Serena MCP Integration (first implementation of this pattern)
- KIT-ADR-0006: Agent Session Initialization Pattern (activation protocol)

## References

- Claude Code MCP Documentation: https://docs.claude.com/en/docs/claude-code
- MCP Protocol Specification: https://modelcontextprotocol.io/
- Serena setup script: `.serena/setup-serena.sh` (reference implementation)

## Revision History

- 2025-11-29: Initial decision (Accepted)
  - Documented four-phase MCP tool addition pattern
  - Established checklist and example integration
  - Defined security considerations and testing approach

---

**Template Version**: 1.1.0
**Last Updated**: 2025-11-29
**Project**: agentive-starter-kit
