# ASK-0015: OpenAPI Specification Strategy ADR

**Status**: Done
**Priority**: low
**Assigned To**: planner
**Estimated Effort**: 2-3 hours
**Created**: 2025-11-28

## Related Tasks

**Parent Task**: None (ADR Migration - Tier 3: API & Quality)
**Depends On**: None
**Blocks**: ASK-0016 (API Versioning)
**Related**: ASK-0017 (API Testing)

## Overview

Adapt and document the OpenAPI Specification Strategy from thematic-cuts (TC ADR-0033) for the agentive-starter-kit. This ADR establishes contract-first API development using OpenAPI 3.1.

**Source**: `thematic-cuts/docs/decisions/adr/ADR-0033-openapi-specification-strategy.md`

**When Needed**: When the project exposes REST APIs that need documentation, validation, and client generation.

## Key Concepts to Document

### Contract-First Development

```
OpenAPI Spec (Single Source of Truth)
    ↓
Generated: Docs, Clients, Validators
    ↓
Implementation must match spec
```

### OpenAPI 3.1 Features

- JSON Schema compatibility
- Webhook support
- Improved type system
- Better nullable handling

### Spec Location

```
api/
├── openapi.yaml          # Main specification
├── schemas/              # Reusable schemas
│   ├── Task.yaml
│   └── Error.yaml
└── paths/                # Endpoint definitions
    └── tasks.yaml
```

### Validation Integration

```python
from openapi_core import validate_request, validate_response

# Middleware validates all requests/responses
@app.middleware("http")
async def validate_openapi(request, call_next):
    validate_request(request, spec)
    response = await call_next(request)
    validate_response(response, spec)
    return response
```

## Requirements

### Functional Requirements
1. Document the OpenAPI strategy as an ADR
2. Explain contract-first benefits
3. Show spec organization pattern
4. Document validation integration

### Non-Functional Requirements
- ADR follows project template
- Applicable when project adds API
- Links to OpenAPI resources

## Acceptance Criteria

### Must Have
- [ ] ADR created following project template
- [ ] Documents contract-first approach
- [ ] Shows spec file organization
- [ ] Explains validation integration
- [ ] Lists tooling recommendations

### Should Have
- [ ] Client generation patterns
- [ ] Documentation generation
- [ ] CI validation of spec

## Implementation Plan

1. **Read source ADR** from thematic-cuts
2. **Adapt for starter-kit** - Generic API guidance
3. **Create ADR** in `docs/decisions/adr/`

## Time Estimate

| Phase | Time |
|-------|------|
| Read source ADR | 30 min |
| Adapt and write | 1.5-2 hours |
| Review and finalize | 30 min |
| **Total** | **2-3 hours** |

## References

- Source: `thematic-cuts/docs/decisions/adr/ADR-0033-openapi-specification-strategy.md`
- OpenAPI 3.1: https://spec.openapis.org/oas/v3.1.0
- openapi-core: https://pypi.org/project/openapi-core/

## Notes

- This ADR is for future API development
- Not needed until project exposes REST endpoints
- Consider FastAPI which has built-in OpenAPI support

---

**Template Version**: 1.0.0
**Created**: 2025-11-28
