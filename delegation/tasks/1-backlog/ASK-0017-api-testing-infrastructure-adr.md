# ASK-0017: Separate API Testing Infrastructure ADR

**Status**: Backlog
**Priority**: low
**Assigned To**: planner
**Estimated Effort**: 2-3 hours
**Created**: 2025-11-28

## Related Tasks

**Parent Task**: None (ADR Migration - Tier 3: API & Quality)
**Depends On**: ASK-0015 (OpenAPI Specification), ASK-0007 (Test Infrastructure)
**Blocks**: None
**Related**: ASK-0016 (API Versioning)

## Overview

Document a dedicated API testing infrastructure for the agentive-starter-kit. This ADR establishes a dedicated test harness for API endpoints, separate from unit tests.

**When Needed**: When the project has REST APIs that need contract validation and integration testing.

## Key Concepts to Document

### Test Separation

```
tests/
├── unit/              # Fast, isolated tests
├── integration/       # Cross-component tests
└── api/               # API-specific tests ← NEW
    ├── conftest.py    # API test fixtures
    ├── test_tasks.py  # Endpoint tests
    └── test_errors.py # Error response tests
```

### API Test Fixtures

```python
# tests/api/conftest.py
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def api_client():
    from myapp import app
    return TestClient(app)

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}
```

### Contract Validation

```python
def test_create_task_matches_schema(api_client, openapi_spec):
    response = api_client.post("/tasks", json={"title": "Test"})
    validate_response(response, openapi_spec, "/tasks", "post")
```

### Test Categories

| Category | Purpose | Speed |
|----------|---------|-------|
| Contract | Schema validation | Fast |
| Smoke | Basic endpoint health | Fast |
| Integration | Full request flow | Medium |
| Load | Performance testing | Slow |

## Acceptance Criteria

### Must Have

- [ ] ADR created following project template
- [ ] Documents test directory structure
- [ ] Shows API test fixtures
- [ ] Explains contract validation
- [ ] Lists test categories

### Should Have

- [ ] CI configuration for API tests
- [ ] Test data management
- [ ] Authentication testing patterns

## Notes

- This ADR is for future API development
- Consider schemathesis for property-based API testing
- Integrates with OpenAPI specification (ASK-0015)

---

**Template Version**: 1.0.0
**Created**: 2025-11-28
