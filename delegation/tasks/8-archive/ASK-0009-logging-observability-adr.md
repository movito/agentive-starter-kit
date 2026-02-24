# ASK-0009: Logging & Observability Architecture ADR

**Status**: Done
**Priority**: medium
**Assigned To**: planner
**Estimated Effort**: 2-3 hours
**Created**: 2025-11-28

## Related Tasks

**Parent Task**: None (ADR Migration - Tier 1)
**Depends On**: None
**Blocks**: None
**Related**: ASK-0008 (Configuration Architecture)

## Overview

Adapt and document the Logging & Observability Architecture from thematic-cuts (TC ADR-0022) for the agentive-starter-kit. This ADR establishes centralized logging with rotation, structured output, and performance monitoring.

**Source**: `thematic-cuts/docs/decisions/adr/ADR-0022-logging-observability-architecture.md`

**Why Essential**: Production-ready logging is crucial for debugging agent behavior and understanding system performance. The pattern supports console output, file rotation, and JSON for APIs.

## Key Concepts to Document

### Logging Architecture

```
Logger Hierarchy:
  agentive                    # Root logger
  agentive.sync               # Linear sync
  agentive.agents             # Agent operations
  agentive.cli                # CLI commands
```

### Output Modes

1. **Console** - Human-readable for development
2. **File** - Rotating logs for persistence
3. **JSON** - Structured for API/machine parsing

### Performance Monitoring

```python
@performance_logged
def slow_operation():
    # Automatically logs execution time
    pass
```

## Requirements

### Functional Requirements
1. Document the logging architecture as an ADR
2. Explain logger naming conventions
3. Document file rotation configuration
4. Cover performance decorator pattern

### Non-Functional Requirements
- ADR follows project template
- Includes practical code examples
- References Python logging best practices

## Acceptance Criteria

### Must Have
- [ ] ADR-0007 created following project template
- [ ] Documents logger hierarchy pattern
- [ ] Explains dual output (console + file)
- [ ] Covers rotating file handler configuration
- [ ] Includes performance logging decorator

### Should Have
- [ ] Example of adding new logger
- [ ] Guidance on log levels
- [ ] Testing with captured logs

## Implementation Plan

1. **Read source ADR** from thematic-cuts
2. **Audit existing logging** in starter-kit
3. **Adapt for starter-kit** - Create practical pattern
4. **Create ADR-0007** in `docs/decisions/adr/`

## Success Metrics

### Quantitative
- ADR created and follows template
- All acceptance criteria met

### Qualitative
- Consistent logging across project
- Debugging made easier

## Time Estimate

| Phase | Time |
|-------|------|
| Read source ADR | 30 min |
| Audit existing logging | 30 min |
| Adapt and write | 1-1.5 hours |
| Review and finalize | 30 min |
| **Total** | **2-3 hours** |

## References

- Source: `thematic-cuts/docs/decisions/adr/ADR-0022-logging-observability-architecture.md`
- Python logging: https://docs.python.org/3/library/logging.html
- 12-factor logs: https://12factor.net/logs

## Notes

- Starter-kit may not have logging infrastructure yet
- This ADR may lead to implementation task
- Consider structlog for structured logging

---

**Template Version**: 1.0.0
**Created**: 2025-11-28
