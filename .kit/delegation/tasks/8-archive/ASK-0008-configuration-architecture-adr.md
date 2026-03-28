# ASK-0008: Configuration Architecture ADR

**Status**: Done
**Priority**: medium
**Assigned To**: planner
**Estimated Effort**: 2-3 hours
**Created**: 2025-11-28

## Related Tasks

**Parent Task**: None (ADR Migration - Tier 1)
**Depends On**: None
**Blocks**: None
**Related**: ASK-0009 (Logging & Observability)

## Overview

Adapt and document the Configuration Architecture from thematic-cuts (TC ADR-0027) for the agentive-starter-kit. This ADR establishes a hierarchical configuration system with validation.

**Source**: `thematic-cuts/docs/decisions/adr/ADR-0027-configuration-architecture.md`

**Why Essential**: Provides a consistent, type-safe way to manage settings across environments. The pattern supports: defaults → user config → environment variables → runtime overrides.

## Key Concepts to Document

### Configuration Hierarchy

```
Priority (lowest to highest):
1. Defaults (in code)
2. User config file (JSON/YAML)
3. Environment variables
4. Runtime arguments
```

### Key Principles

1. **Type safety** - Configuration validated at load time
2. **Environment-friendly** - 12-factor app compatible
3. **Discoverable** - Clear precedence rules
4. **Testable** - Easy to override in tests

### Configuration Locations

```
.env                     # Environment variables (gitignored)
.env.template            # Template for required vars
config/                  # User configuration files
pyproject.toml           # Tool configuration
```

## Requirements

### Functional Requirements
1. Document the configuration hierarchy as an ADR
2. Explain precedence rules clearly
3. Show how to add new configuration options
4. Document validation approach

### Non-Functional Requirements
- ADR follows project template
- Practical examples included
- Security considerations for secrets

## Acceptance Criteria

### Must Have
- [ ] ADR-0006 created following project template
- [ ] Documents 4-level configuration hierarchy
- [ ] Explains environment variable handling
- [ ] Covers .env and .env.template patterns
- [ ] References existing configuration files

### Should Have
- [ ] Example of adding new config option
- [ ] Validation pattern examples
- [ ] Testing guidance for config

## Implementation Plan

1. **Read source ADR** from thematic-cuts
2. **Audit existing config** in starter-kit (.env.template, pyproject.toml)
3. **Adapt for starter-kit** - Match current patterns
4. **Create ADR-0006** in `docs/decisions/adr/`

## Success Metrics

### Quantitative
- ADR created and follows template
- All acceptance criteria met

### Qualitative
- Clear guidance for adding configuration
- Security-conscious patterns documented

## Time Estimate

| Phase | Time |
|-------|------|
| Read source ADR | 30 min |
| Audit existing config | 30 min |
| Adapt and write | 1-1.5 hours |
| Review and finalize | 30 min |
| **Total** | **2-3 hours** |

## References

- Source: `thematic-cuts/docs/decisions/adr/ADR-0027-configuration-architecture.md`
- Existing: `.env.template`, `pyproject.toml`
- python-dotenv: https://pypi.org/project/python-dotenv/

## Notes

- Starter-kit uses python-dotenv for .env loading
- Focus on documenting the pattern, not implementing new code
- Consider Pydantic for validation in future

---

**Template Version**: 1.0.0
**Created**: 2025-11-28
