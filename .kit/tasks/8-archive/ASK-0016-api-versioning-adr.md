# ASK-0016: API Versioning Strategy ADR

**Status**: Done
**Priority**: low
**Assigned To**: planner
**Estimated Effort**: 1-2 hours
**Created**: 2025-11-28

## Related Tasks

**Parent Task**: None (ADR Migration - Tier 3: API & Quality)
**Depends On**: ASK-0015 (OpenAPI Specification)
**Blocks**: None
**Related**: ASK-0017 (API Testing)

## Overview

Adapt and document the API Versioning Strategy from thematic-cuts (TC ADR-0034) for the agentive-starter-kit. This ADR establishes date-based versioning (YYYY-MM-DD) with clear deprecation timelines.

**Source**: `thematic-cuts/docs/decisions/adr/ADR-0034-api-versioning-strategy.md`

**When Needed**: When the project has external API consumers who need stability guarantees.

## Key Concepts to Document

### Date-Based Versioning

```
API-Version: 2025-11-28

Benefits:
- Natural chronological ordering
- Clear "age" of version
- No semantic ambiguity (v1 vs v2)
```

### Version Header

```http
GET /api/tasks HTTP/1.1
Host: api.example.com
API-Version: 2025-11-28
```

### Deprecation Policy

| Timeline | Action |
|----------|--------|
| Day 0 | New version released |
| Month 3 | Old version deprecated (warning headers) |
| Month 6 | Old version sunset (404) |

### Version Negotiation

```python
@app.middleware("http")
async def version_middleware(request, call_next):
    version = request.headers.get("API-Version", LATEST_VERSION)
    if version < MINIMUM_VERSION:
        return JSONResponse(
            {"error": "API version no longer supported"},
            status_code=410
        )
    request.state.api_version = version
    return await call_next(request)
```

## Requirements

### Functional Requirements
1. Document the versioning strategy as an ADR
2. Explain date-based format benefits
3. Define deprecation timeline
4. Show version negotiation pattern

### Non-Functional Requirements
- ADR follows project template
- Clear policy for API consumers
- Migration guidance included

## Acceptance Criteria

### Must Have
- [ ] ADR created following project template
- [ ] Documents date-based version format
- [ ] Defines deprecation timeline (6 months)
- [ ] Shows version header pattern
- [ ] Explains sunset process

### Should Have
- [ ] Migration guide template
- [ ] Changelog requirements
- [ ] Client notification pattern

## Implementation Plan

1. **Read source ADR** from thematic-cuts
2. **Adapt for starter-kit** - Generic versioning guidance
3. **Create ADR** in `docs/decisions/adr/`

## Time Estimate

| Phase | Time |
|-------|------|
| Read source ADR | 20 min |
| Adapt and write | 1 hour |
| Review and finalize | 20 min |
| **Total** | **1-2 hours** |

## References

- Source: `thematic-cuts/docs/decisions/adr/ADR-0034-api-versioning-strategy.md`
- Stripe API versioning: https://stripe.com/docs/api/versioning
- API versioning best practices: https://www.postman.com/api-platform/api-versioning/

## Notes

- This ADR is for future API development
- Date-based versioning inspired by Stripe
- Alternative: semantic versioning (v1, v2)

---

**Template Version**: 1.0.0
**Created**: 2025-11-28
