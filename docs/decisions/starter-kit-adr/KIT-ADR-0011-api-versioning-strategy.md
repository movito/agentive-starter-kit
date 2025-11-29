# KIT-ADR-0011: API Versioning Strategy

**Status**: Accepted

**Date**: 2025-11-28

**Deciders**: planner, User

## Context

### Problem Statement

When APIs evolve, breaking changes are inevitable. We need a versioning strategy that:
- Gives consumers stability guarantees
- Allows controlled deprecation of old versions
- Provides clear migration paths
- Is simple to implement and understand

### Forces at Play

**Technical Requirements:**
- Support multiple API versions simultaneously
- Clear version identification in requests
- Automated deprecation warnings
- Graceful sunset of old versions

**Constraints:**
- Must work with REST APIs
- Should integrate with OpenAPI (KIT-ADR-0010)
- Must be implementable in Python frameworks

**Assumptions:**
- APIs will have external consumers
- Breaking changes will occur over time
- Consumers need migration time

## Decision

We will adopt **date-based API versioning** (YYYY-MM-DD format) with a **6-month deprecation policy**.

### Core Principles

1. **Date-based versions**: Clear chronological ordering
2. **Header-based**: Version specified in `API-Version` header
3. **Predictable deprecation**: 3-month warning, 6-month sunset
4. **Latest by default**: Missing header uses latest version

### Implementation Details

**Version Format:**

```
YYYY-MM-DD

Examples:
- 2025-11-28
- 2026-03-15
- 2026-06-01
```

**Why date-based (like Stripe)?**
- Natural chronological ordering
- Clear "age" of version
- No semantic ambiguity (what's in v2 vs v3?)
- Easy to compare versions programmatically

**Request Header:**

```http
GET /api/tasks HTTP/1.1
Host: api.example.com
API-Version: 2025-11-28
Accept: application/json
```

**Deprecation Timeline:**

| Timeline | Action | Response Header |
|----------|--------|-----------------|
| Day 0 | New version released | - |
| Month 3 | Old version deprecated | `Deprecation: true` |
| Month 4-5 | Warning period | `Sunset: <date>` |
| Month 6 | Old version sunset | 410 Gone |

**Version Middleware (FastAPI):**

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta

app = FastAPI()

# Version configuration
VERSIONS = {
    "2025-11-28": {"status": "current"},
    "2025-06-01": {"status": "deprecated", "sunset": "2025-12-01"},
    "2025-01-15": {"status": "sunset"},
}
LATEST_VERSION = "2025-11-28"
MINIMUM_VERSION = "2025-06-01"

@app.middleware("http")
async def version_middleware(request: Request, call_next):
    # Get version from header (default to latest)
    version = request.headers.get("API-Version", LATEST_VERSION)

    # Check if version exists
    if version not in VERSIONS:
        return JSONResponse(
            {"error": f"Unknown API version: {version}"},
            status_code=400
        )

    version_info = VERSIONS[version]

    # Handle sunset versions
    if version_info["status"] == "sunset":
        return JSONResponse(
            {
                "error": "API version no longer supported",
                "message": f"Version {version} was sunset. Use {LATEST_VERSION}.",
                "migration_guide": f"/docs/migration/{version}-to-{LATEST_VERSION}"
            },
            status_code=410  # Gone
        )

    # Store version in request state
    request.state.api_version = version

    # Process request
    response = await call_next(request)

    # Add deprecation headers if needed
    if version_info["status"] == "deprecated":
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = version_info["sunset"]
        response.headers["Link"] = f'</docs/migration/{version}>; rel="deprecation"'

    return response
```

**OpenAPI Integration:**

```yaml
# api/openapi.yaml
openapi: 3.1.0
info:
  title: Agentive API
  version: "2025-11-28"

paths:
  /tasks:
    get:
      parameters:
        - name: API-Version
          in: header
          required: false
          schema:
            type: string
            pattern: '^\d{4}-\d{2}-\d{2}$'
            default: "2025-11-28"
          description: API version (YYYY-MM-DD format)
```

**Changelog Requirements:**

Each version must have a changelog entry:

```markdown
# API Changelog

## 2025-11-28 (Current)

### Breaking Changes
- Removed `legacy_field` from Task response

### New Features
- Added `metadata` field to Task

### Migration Guide
- Replace `legacy_field` with `new_field`
- See: /docs/migration/2025-06-01-to-2025-11-28

## 2025-06-01 (Deprecated)
...
```

**Client Notification Pattern:**

```python
# Deprecation warning in response
{
    "data": { ... },
    "_meta": {
        "api_version": "2025-06-01",
        "deprecation_warning": "This API version is deprecated",
        "sunset_date": "2025-12-01",
        "migration_guide": "/docs/migration/2025-06-01"
    }
}
```

## Consequences

### Positive

- ✅ **Clear timeline**: Dates are unambiguous
- ✅ **Predictable deprecation**: 6-month policy is industry standard
- ✅ **Header-based**: Doesn't pollute URLs
- ✅ **Stripe-inspired**: Proven pattern at scale

### Negative

- ⚠️ **Multiple versions**: Must maintain code for supported versions
- ⚠️ **Date tracking**: Need to track version dates carefully
- ⚠️ **Client awareness**: Clients must read deprecation headers

### Neutral

- 📊 **Changelog overhead**: Must document each version's changes
- 📊 **Migration guides**: Required for breaking changes

## Alternatives Considered

### Alternative 1: URL-Based Versioning (/v1/, /v2/)

**Description**: Version in URL path like `/v1/tasks`

**Not adopted because**:
- ❌ Pollutes URL namespace
- ❌ Unclear what's in each version
- ❌ Harder to deprecate gracefully
- ✅ Simple for consumers (may use if needed)

### Alternative 2: Semantic Versioning (v1.2.3)

**Description**: Full semver for API versions

**Not adopted because**:
- ❌ Overkill for API versioning
- ❌ Minor/patch versions rarely matter for APIs
- ❌ Consumers typically pin to major version anyway

### Alternative 3: No Versioning

**Description**: Single version, break things as needed

**Rejected because**:
- ❌ Terrible for external consumers
- ❌ No migration time
- ❌ Unprofessional

## Implementation Status

**Current State**: No REST APIs exist

**When to Apply**: When adding first REST endpoint with external consumers

**First Steps**:
1. Add version middleware
2. Document initial version in changelog
3. Include version in OpenAPI spec

## Related Decisions

- KIT-ADR-0010: OpenAPI Specification Strategy (version in spec)

## References

- Stripe API Versioning: https://stripe.com/docs/api/versioning
- Zalando API Guidelines: https://opensource.zalando.com/restful-api-guidelines/#api-versioning
- Microsoft REST API Guidelines: https://github.com/microsoft/api-guidelines

## Revision History

- 2025-11-28: Initial decision (Accepted)
  - Adopted date-based versioning (YYYY-MM-DD)
  - Established 6-month deprecation policy
  - Documented middleware implementation

---

**Template Version**: 1.1.0
**Last Updated**: 2025-11-28
**Project**: agentive-starter-kit
