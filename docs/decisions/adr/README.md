# Architecture Decision Records (ADRs)

This directory is for **your project's** architectural decisions. Start fresh with `ADR-0001`.

## Starter Kit Reference

The agentive-starter-kit includes reference ADRs in `docs/decisions/starter-kit-adr/`. These document the patterns you inherit:

| Prefix | Location | Purpose |
|--------|----------|---------|
| `KIT-ADR-XXXX` | `starter-kit-adr/` | Starter kit patterns (reference) |
| `ADR-XXXX` | `adr/` (here) | Your project decisions |

See [starter-kit-adr/README.md](../starter-kit-adr/README.md) for the full index.

## What are ADRs?

ADRs capture important architectural decisions along with their context and consequences:
- **Context**: The forces and factors influencing the decision
- **Decision**: What was decided and why
- **Consequences**: The positive, negative, and neutral implications

ADRs are **immutable** once accepted. If a decision changes, create a new ADR that supersedes the old one.

## Format

Use `TEMPLATE-FOR-ADR-FILES.md` in this directory. Key sections:

```markdown
# ADR-####: Title

**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-XXXX

**Date**: YYYY-MM-DD

**Deciders**: [Decision makers]

## Context
[Forces, factors, and constraints influencing the decision]

## Decision
[What we decided and why]

## Consequences
### Positive
### Negative
### Neutral
```

## Naming Convention

**Format**: `ADR-####-description.md`
- `ADR-` prefix (required)
- `####` four-digit number (0001, 0002, etc.)
- `-description` kebab-case summary

**Examples**:
- `ADR-0001-user-authentication-strategy.md`
- `ADR-0002-database-selection.md`

## Your Project's ADRs

| ADR | Title | Date | Status |
|-----|-------|------|--------|
| *Start with ADR-0001* | | | |

## When to Write an ADR

**Write an ADR when:**
- Making architectural choices that affect project structure
- Choosing between competing technical approaches
- Establishing patterns or conventions
- Making trade-offs with significant implications

**Don't write an ADR for:**
- Routine bug fixes
- Feature implementations following established patterns
- Temporary experimental code
- Configuration changes without architectural impact

## Superseding Starter Kit Patterns

If you need to change a pattern from the starter kit:

1. Create a new ADR here explaining your change
2. Reference the `KIT-ADR-XXXX` you're superseding
3. Document the rationale for diverging

Example:
```markdown
# ADR-0001: Custom Logging Format

**Status**: Accepted
**Supersedes**: KIT-ADR-0009 (Logging & Observability)

## Context
We need JSON-structured logs for our cloud monitoring system...
```

## References

- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) - Michael Nygard
- [ADR GitHub Organization](https://adr.github.io/) - ADR tools and resources

---

**Template**: agentive-starter-kit
**Your Project**: [Your project name]
**Started**: [Date you cloned the starter kit]
