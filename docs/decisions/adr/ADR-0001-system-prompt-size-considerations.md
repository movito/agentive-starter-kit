# ADR-0001: System Prompt Size Considerations

**Status**: Accepted
**Date**: 2025-11-25
**Context**: Agent launcher passes full agent markdown as system prompt

## Context

The agentive-starter-kit uses a launcher script (`agents/launch`) that passes the entire agent markdown file as a system prompt via `--append-system-prompt`. Large agent definitions can increase request processing time and make API overload errors more likely.

### Observed Issue

On 2025-11-25, a large agent file (~500 lines, ~17KB) triggered repeated `overloaded_error` responses:

```json
{"type":"error","error":{"type":"overloaded_error","message":"Overloaded"},"request_id":null}
```

The error resolved after ~7 retry attempts (approximately 3-4 minutes).

### Root Cause Analysis

The `overloaded_error` is an Anthropic API capacity issue, not a prompt size error. However:
- Larger system prompts increase request payload size
- More tokens require more processing time
- During high-demand periods, larger requests may be more susceptible to overload rejection

## Decision

**Keep the embedded system prompt approach** but:
1. Separate concerns into dedicated agents (e.g., onboarding agent vs coordinator)
2. Document guidelines for agent size management
3. Use lighter models (Sonnet) for simpler tasks

### Agent Size Guidelines

| Agent Type | Recommended Max | Model | Notes |
|------------|-----------------|-------|-------|
| Coordinator agents | 400 lines | Opus | Complex workflows |
| Specialized agents | 250 lines | Sonnet | Single responsibility |
| Simple/utility agents | 150 lines | Sonnet | Minimal context |

### Separation of Concerns

Rather than one large agent handling everything, split responsibilities:
- **onboarding agent**: First-run setup only (dedicated, focused)
- **planner agent**: Project coordination (no setup code)
- **feature-developer**: Implementation only

This naturally keeps each agent file smaller and more focused.

### Mitigation Options (if issues persist)

1. **Externalize verbose content**: Move detailed instructions to `.agent-context/` files that agents read on demand
2. **Lazy loading**: Agent reads detailed context only when needed
3. **Model selection**: Use lighter models for less complex agents

### When to Externalize Content

Consider moving content to external files if:
- Agent markdown exceeds 500 lines
- Repeated overload errors occur (>5 retries)
- Content is rarely needed (e.g., reference documentation)

## Consequences

### Positive
- Simple architecture (single file per agent)
- All context immediately available to agent
- Easy to version and review
- Separation of concerns keeps files manageable

### Negative
- Larger request payload for complex agents
- Potentially longer time-to-first-response
- More susceptible to overload during high-demand periods

### Monitoring

Track these indicators:
- Retry attempts before successful connection
- Time-to-first-response for different agents
- Agent file sizes over time

## Related

- `agents/launch` - Agent launcher script
- `agents/onboarding` - First-run setup launcher
- `.claude/agents/` - Agent definition files
- Anthropic API documentation on rate limits
