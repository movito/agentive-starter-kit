# KIT-ADR-0010: OpenAPI Specification Strategy

**Status**: Accepted

**Date**: 2025-11-28

**Deciders**: planner, User

## Context

### Problem Statement

When the project adds REST APIs, we need a consistent approach for:
- API documentation that stays in sync with implementation
- Request/response validation
- Client SDK generation
- Contract-first development workflow

Without a clear strategy, APIs tend to drift from documentation, leading to integration issues and poor developer experience.

### Forces at Play

**Technical Requirements:**
- Machine-readable API specification
- Auto-generated documentation
- Request/response validation
- Support for modern Python frameworks (FastAPI, Flask)

**Constraints:**
- Specification must be version-controlled
- Should work with CI/CD pipelines
- Must support incremental adoption

**Assumptions:**
- Future APIs will be RESTful
- Python will be the primary implementation language
- APIs may need to support external consumers

## Decision

We will adopt **OpenAPI 3.1** with a **contract-first development** approach when adding REST APIs.

### Core Principles

1. **Spec is source of truth**: OpenAPI specification defines the contract
2. **Contract-first**: Design API in spec before implementation
3. **Automated validation**: Middleware validates requests/responses against spec
4. **Generated artifacts**: Docs and clients generated from spec

### Implementation Details

**Specification Location:**

```
api/
├── openapi.yaml          # Main specification file
├── schemas/              # Reusable schema definitions
│   ├── Task.yaml         # Task resource schema
│   ├── Error.yaml        # Error response schema
│   └── common.yaml       # Shared definitions
└── paths/                # Endpoint definitions (optional split)
    ├── tasks.yaml
    └── health.yaml
```

**OpenAPI 3.1 Template:**

```yaml
openapi: 3.1.0
info:
  title: Agentive Starter Kit API
  version: 1.0.0
  description: |
    API for the agentive starter kit.

servers:
  - url: http://localhost:8000
    description: Local development
  - url: https://api.example.com
    description: Production

paths:
  /health:
    get:
      operationId: getHealth
      summary: Health check endpoint
      responses:
        '200':
          description: Service is healthy
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'

components:
  schemas:
    HealthResponse:
      type: object
      required:
        - status
      properties:
        status:
          type: string
          enum: [healthy, degraded, unhealthy]
        timestamp:
          type: string
          format: date-time

    Error:
      type: object
      required:
        - code
        - message
      properties:
        code:
          type: string
        message:
          type: string
        details:
          type: object
```

**Framework Integration (FastAPI - Recommended):**

```python
# FastAPI auto-generates OpenAPI from code
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Agentive Starter Kit API",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",        # Swagger UI
    redoc_url="/redoc",      # ReDoc
)

class HealthResponse(BaseModel):
    status: str
    timestamp: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat()
    )
```

**Validation Middleware (Manual OpenAPI):**

```python
# For non-FastAPI frameworks
from openapi_core import OpenAPI
from openapi_core.contrib.starlette import StarletteOpenAPIMiddleware

# Load specification
spec = OpenAPI.from_file_path("api/openapi.yaml")

# Add validation middleware
app.add_middleware(StarletteOpenAPIMiddleware, openapi=spec)
```

**CI Validation:**

```yaml
# .github/workflows/api.yml
- name: Validate OpenAPI Spec
  run: |
    pip install openapi-spec-validator
    openapi-spec-validator api/openapi.yaml

- name: Check for breaking changes
  run: |
    pip install oasdiff
    oasdiff breaking api/openapi.yaml api/openapi-previous.yaml
```

**Development Workflow:**

```
1. Design API in openapi.yaml
    ↓
2. Review spec in Swagger Editor
    ↓
3. Implement endpoints matching spec
    ↓
4. Validation middleware enforces contract
    ↓
5. Generate client SDKs if needed
```

**Tooling Recommendations:**

| Purpose | Tool | Notes |
|---------|------|-------|
| Framework | FastAPI | Built-in OpenAPI, Pydantic validation |
| Spec editing | Swagger Editor | Visual editor, validation |
| Validation | openapi-core | Runtime validation middleware |
| Breaking changes | oasdiff | CI check for API compatibility |
| Client generation | openapi-generator | Multi-language SDK generation |
| Documentation | Redoc / Swagger UI | Auto-generated from spec |

## Consequences

### Positive

- ✅ **Single source of truth**: Spec defines the contract
- ✅ **Auto-documentation**: Always up-to-date API docs
- ✅ **Validation**: Request/response validated automatically
- ✅ **Client generation**: SDKs from spec
- ✅ **Breaking change detection**: CI catches incompatibilities

### Negative

- ⚠️ **Learning curve**: OpenAPI syntax takes time to learn
- ⚠️ **Spec maintenance**: Must keep spec updated
- ⚠️ **Tooling complexity**: Multiple tools to configure

### Neutral

- 📊 **FastAPI preference**: Built-in OpenAPI simplifies adoption
- 📊 **Future readiness**: Documented for when APIs are added

## Alternatives Considered

### Alternative 1: Code-First (No Spec)

**Description**: Document APIs manually, no formal specification

**Rejected because**:
- ❌ Documentation drifts from implementation
- ❌ No automated validation
- ❌ No client generation

### Alternative 2: GraphQL

**Description**: Use GraphQL instead of REST with OpenAPI

**Not adopted because**:
- ❌ Different paradigm, higher learning curve
- ❌ Overkill for simple CRUD APIs
- ✅ Consider for complex data requirements

### Alternative 3: OpenAPI 3.0

**Description**: Use OpenAPI 3.0 instead of 3.1

**Rejected because**:
- ❌ 3.0 has JSON Schema incompatibilities
- ❌ 3.1 has better nullable handling
- ❌ 3.1 is the current standard

## Implementation Status

**Current State**: No REST APIs exist

**When to Apply**: When adding first REST endpoint

**Recommended First Steps**:
1. Choose framework (FastAPI recommended)
2. Create `api/openapi.yaml` or use FastAPI auto-generation
3. Add CI validation workflow
4. Document in project README

## Related Decisions

- KIT-ADR-0005: Test Infrastructure (API tests)
- ADR-0018: Validation Architecture (Pydantic patterns)

## References

- OpenAPI 3.1 Specification: https://spec.openapis.org/oas/v3.1.0
- FastAPI: https://fastapi.tiangolo.com/
- openapi-core: https://pypi.org/project/openapi-core/
- Swagger Editor: https://editor.swagger.io/
- oasdiff: https://github.com/Tufin/oasdiff

## Revision History

- 2025-11-28: Initial decision (Accepted)
  - Documented OpenAPI 3.1 strategy
  - Recommended FastAPI for implementation
  - Established contract-first workflow

---

**Template Version**: 1.1.0
**Last Updated**: 2025-11-28
**Project**: agentive-starter-kit
