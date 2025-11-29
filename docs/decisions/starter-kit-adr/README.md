# Starter Kit Architecture Decision Records

This folder contains ADRs inherited from the **agentive-starter-kit** template. These document the architectural decisions made for the starter kit infrastructure.

## For Users of This Template

**These ADRs are read-only reference material.** They document patterns and decisions you inherit when using the starter kit:

- Agent initialization patterns
- Code review workflows
- Task management with Linear
- Logging and configuration architecture
- And more...

**Your project's ADRs belong in `docs/decisions/adr/`** - start fresh with `ADR-0001`.

## Naming Convention

| Prefix | Location | Purpose |
|--------|----------|---------|
| `KIT-ADR-XXXX` | `starter-kit-adr/` | Starter kit infrastructure decisions (reference) |
| `ADR-XXXX` | `adr/` | Your project-specific decisions |

## Index

| ID | Title | Status |
|----|-------|--------|
| KIT-ADR-0001 | System Prompt Size Considerations | Accepted |
| KIT-ADR-0002 | Serena MCP Integration | Accepted |
| KIT-ADR-0003 | Linear Sync vs MCP | Accepted |
| KIT-ADR-0004 | Adversarial Workflow Integration | Accepted |
| KIT-ADR-0005 | Test Infrastructure Strategy | Accepted |
| KIT-ADR-0006 | Agent Session Initialization | Accepted |
| KIT-ADR-0007 | Dependabot Automation | Accepted |
| KIT-ADR-0008 | Configuration Architecture | Accepted |
| KIT-ADR-0009 | Logging & Observability | Accepted |
| KIT-ADR-0010 | OpenAPI Specification Strategy | Accepted |
| KIT-ADR-0011 | API Versioning Strategy | Accepted |
| KIT-ADR-0012 | Task Status Linear Alignment | Accepted |
| KIT-ADR-0013 | Real-Time Task Monitoring | Accepted |
| KIT-ADR-0014 | Code Review Workflow | Accepted |
| KIT-ADR-0015 | MCP Tool Addition Pattern | Accepted |
| KIT-ADR-0016 | Validation Architecture | Accepted |
| KIT-ADR-0017 | API Testing Infrastructure | Accepted |
| KIT-ADR-0018 | Workflow Observation | Accepted |

## When to Reference These

Reference these KIT-ADRs when:
- Understanding how the starter kit works
- Deciding whether to adopt or modify a pattern
- Training agents on project conventions
- Onboarding new team members

## Modifying Starter Kit Patterns

If you need to change a pattern from the starter kit:

1. **Create a new ADR** in `docs/decisions/adr/` explaining your change
2. **Reference the KIT-ADR** you're superseding
3. **Document the rationale** for diverging

Example:
```markdown
# ADR-0001: Custom Logging Format

**Status**: Accepted
**Supersedes**: KIT-ADR-0009 (Logging & Observability)

## Context
We need JSON-structured logs for our monitoring system...
```

---

**Template**: agentive-starter-kit
**Last Updated**: 2025-11-29
