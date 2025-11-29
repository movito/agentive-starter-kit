# KIT-ADR-0017: API Testing Infrastructure

**Status**: Accepted

**Date**: 2025-11-29

**Deciders**: planner, User

## Context

### Problem Statement

API endpoints require testing at multiple levels: contract validation against OpenAPI specs, integration testing with dependencies, and load testing for performance. Mixing API tests with unit tests creates problems:
- Different test speeds and resource needs
- Unclear test organization
- Missing contract validation
- Hard to run API tests in isolation

### Forces at Play

**Technical Requirements:**
- Validate API responses match OpenAPI specification
- Test authentication and authorization
- Integration tests with actual services
- Performance testing under load
- Fast feedback during development

**Constraints:**
- Tests should run in CI pipeline
- Some tests need external services (databases, etc.)
- Contract tests need OpenAPI spec file
- Load tests are slow and resource-intensive

**Assumptions:**
- Project has or will have REST API endpoints
- OpenAPI specification exists (see KIT-ADR-0010)
- Using pytest as the test framework
- FastAPI or similar for API implementation

## Decision

We will establish a **dedicated API testing infrastructure** with clear separation by test type and a shared fixture system.

### Core Principles

1. **Separation by purpose**: Different directories for different test types
2. **Shared fixtures**: Common API fixtures in `tests/api/conftest.py`
3. **Contract-first**: Validate against OpenAPI spec
4. **Incremental depth**: From smoke tests to load tests

### Directory Structure

```
tests/
├── unit/                    # Fast, isolated tests
│   └── ...
├── integration/             # Cross-component tests
│   └── ...
└── api/                     # API-specific tests
    ├── conftest.py          # API test fixtures
    ├── test_health.py       # Health/smoke endpoints
    ├── test_tasks.py        # Task endpoint tests
    ├── test_errors.py       # Error response tests
    ├── test_auth.py         # Authentication tests
    ├── contract/            # OpenAPI contract tests
    │   ├── conftest.py      # Contract-specific fixtures
    │   └── test_schema.py   # Schema validation tests
    └── load/                # Performance tests
        ├── conftest.py      # Load test fixtures
        └── test_throughput.py
```

### Implementation Details

**API Test Fixtures**

```python
# tests/api/conftest.py
import pytest
from fastapi.testclient import TestClient
from typing import Generator

@pytest.fixture(scope="module")
def api_client() -> Generator[TestClient, None, None]:
    """
    Create a test client for API testing.

    Module-scoped for efficiency across test functions.
    """
    from myapp import create_app

    app = create_app(testing=True)
    with TestClient(app) as client:
        yield client


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Standard authentication headers for testing."""
    return {"Authorization": "Bearer test-token-12345"}


@pytest.fixture
def admin_headers() -> dict[str, str]:
    """Admin authentication headers."""
    return {"Authorization": "Bearer admin-token-12345"}


@pytest.fixture
def sample_task() -> dict:
    """Sample task payload for testing."""
    return {
        "id": "TSK-001",
        "title": "Test Task",
        "status": "Todo",
        "priority": "high"
    }
```

**Smoke/Health Tests**

```python
# tests/api/test_health.py
"""
Smoke tests for API health endpoints.

These tests should be fast and verify basic functionality.
Run these first to catch fundamental issues.
"""

def test_health_endpoint(api_client):
    """Health endpoint should return 200 OK."""
    response = api_client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_endpoint(api_client):
    """Readiness endpoint should indicate service is ready."""
    response = api_client.get("/ready")

    assert response.status_code == 200
    assert response.json()["ready"] is True


def test_api_version(api_client):
    """API should return version in headers."""
    response = api_client.get("/health")

    assert "X-API-Version" in response.headers
```

**CRUD Endpoint Tests**

```python
# tests/api/test_tasks.py
"""
Task API endpoint tests.

Tests full lifecycle: create, read, update, delete.
"""
import pytest

class TestTaskEndpoints:
    """Tests for /tasks endpoints."""

    def test_create_task(self, api_client, auth_headers, sample_task):
        """POST /tasks should create a new task."""
        response = api_client.post(
            "/tasks",
            json=sample_task,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == sample_task["id"]
        assert data["title"] == sample_task["title"]

    def test_get_task(self, api_client, auth_headers):
        """GET /tasks/{id} should return task."""
        response = api_client.get("/tasks/TSK-001", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["id"] == "TSK-001"

    def test_update_task(self, api_client, auth_headers):
        """PATCH /tasks/{id} should update task."""
        response = api_client.patch(
            "/tasks/TSK-001",
            json={"status": "In Progress"},
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["status"] == "In Progress"

    def test_delete_task(self, api_client, auth_headers):
        """DELETE /tasks/{id} should remove task."""
        response = api_client.delete("/tasks/TSK-001", headers=auth_headers)

        assert response.status_code == 204

    def test_get_deleted_task_returns_404(self, api_client, auth_headers):
        """GET deleted task should return 404."""
        response = api_client.get("/tasks/TSK-001", headers=auth_headers)

        assert response.status_code == 404


class TestTaskValidation:
    """Tests for task input validation."""

    def test_create_task_missing_title(self, api_client, auth_headers):
        """Creating task without title should fail."""
        response = api_client.post(
            "/tasks",
            json={"id": "TSK-002"},
            headers=auth_headers
        )

        assert response.status_code == 422
        assert "title" in response.text.lower()

    def test_create_task_invalid_status(self, api_client, auth_headers):
        """Creating task with invalid status should fail."""
        response = api_client.post(
            "/tasks",
            json={"id": "TSK-002", "title": "Test", "status": "invalid"},
            headers=auth_headers
        )

        assert response.status_code == 422
```

**Error Response Tests**

```python
# tests/api/test_errors.py
"""
Error response tests.

Verify that errors are returned in consistent format.
"""

def test_404_format(api_client, auth_headers):
    """404 errors should return structured response."""
    response = api_client.get("/tasks/nonexistent", headers=auth_headers)

    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "message" in data


def test_401_unauthorized(api_client):
    """Requests without auth should return 401."""
    response = api_client.get("/tasks")

    assert response.status_code == 401
    assert "error" in response.json()


def test_403_forbidden(api_client, auth_headers):
    """Insufficient permissions should return 403."""
    response = api_client.delete("/admin/users/1", headers=auth_headers)

    assert response.status_code == 403


def test_validation_error_format(api_client, auth_headers):
    """Validation errors should include field details."""
    response = api_client.post(
        "/tasks",
        json={},  # Missing required fields
        headers=auth_headers
    )

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data or "errors" in data
```

**Contract Validation Tests**

```python
# tests/api/contract/conftest.py
import pytest
import yaml
from pathlib import Path

@pytest.fixture(scope="session")
def openapi_spec() -> dict:
    """Load OpenAPI specification."""
    spec_path = Path(__file__).parent.parent.parent.parent / "openapi.yaml"
    with open(spec_path) as f:
        return yaml.safe_load(f)


@pytest.fixture
def schema_validator(openapi_spec):
    """Create schema validator from OpenAPI spec."""
    from openapi_core import OpenAPI
    return OpenAPI.from_dict(openapi_spec)
```

```python
# tests/api/contract/test_schema.py
"""
OpenAPI contract validation tests.

Ensures API responses match the OpenAPI specification.
"""
from openapi_core.testing.mock import MockRequest, MockResponse

def test_task_response_matches_schema(api_client, auth_headers, schema_validator):
    """Task response should match OpenAPI schema."""
    response = api_client.get("/tasks/TSK-001", headers=auth_headers)

    # Validate response against spec
    result = schema_validator.unmarshal_response(
        MockRequest("GET", "/tasks/{task_id}"),
        MockResponse(response.status_code, response.text)
    )

    assert not result.errors, f"Schema errors: {result.errors}"


def test_task_list_matches_schema(api_client, auth_headers, schema_validator):
    """Task list response should match OpenAPI schema."""
    response = api_client.get("/tasks", headers=auth_headers)

    result = schema_validator.unmarshal_response(
        MockRequest("GET", "/tasks"),
        MockResponse(response.status_code, response.text)
    )

    assert not result.errors


def test_error_response_matches_schema(api_client, auth_headers, schema_validator):
    """Error responses should match OpenAPI error schema."""
    response = api_client.get("/tasks/nonexistent", headers=auth_headers)

    result = schema_validator.unmarshal_response(
        MockRequest("GET", "/tasks/{task_id}"),
        MockResponse(response.status_code, response.text)
    )

    # 404 response should still match schema
    assert not result.errors
```

**Load Testing (Optional)**

```python
# tests/api/load/conftest.py
import pytest

@pytest.fixture
def load_client():
    """Client configured for load testing."""
    import httpx
    return httpx.Client(
        base_url="http://localhost:8000",
        timeout=30.0
    )


# tests/api/load/test_throughput.py
"""
Load tests for API throughput.

These tests are slow and should be run separately.
Mark with @pytest.mark.slow or use separate CI job.
"""
import pytest
import time
from concurrent.futures import ThreadPoolExecutor

@pytest.mark.slow
def test_concurrent_reads(load_client, auth_headers):
    """API should handle concurrent read requests."""
    def make_request():
        return load_client.get("/tasks", headers=auth_headers)

    start = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(100)]
        results = [f.result() for f in futures]
    elapsed = time.time() - start

    success_rate = sum(1 for r in results if r.status_code == 200) / len(results)

    assert success_rate >= 0.99, f"Success rate {success_rate} below threshold"
    assert elapsed < 10, f"Took {elapsed}s, expected < 10s"
```

### Test Categories and CI Integration

**pytest.ini Configuration**

```ini
[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    contract: marks tests as contract tests
    load: marks tests as load tests

testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

**CI Pipeline Configuration**

```yaml
# .github/workflows/test.yml
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -e ".[dev]"
      - run: pytest tests/unit -v

  api-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        # ... service config
    steps:
      - uses: actions/checkout@v4
      - run: pip install -e ".[dev]"
      - run: pytest tests/api -v -m "not slow"

  contract-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -e ".[dev]"
      - run: pytest tests/api/contract -v

  load-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'  # Nightly only
    steps:
      - uses: actions/checkout@v4
      - run: pip install -e ".[dev]"
      - run: pytest tests/api/load -v
```

### Test Data Management

**Factory Pattern for Test Data**

```python
# tests/api/factories.py
from typing import Optional
import uuid

def create_task(
    id: Optional[str] = None,
    title: str = "Test Task",
    status: str = "Todo",
    priority: str = "medium"
) -> dict:
    """Factory for creating task test data."""
    return {
        "id": id or f"TSK-{uuid.uuid4().hex[:6].upper()}",
        "title": title,
        "status": status,
        "priority": priority
    }


def create_user(
    email: Optional[str] = None,
    role: str = "user"
) -> dict:
    """Factory for creating user test data."""
    return {
        "email": email or f"test-{uuid.uuid4().hex[:8]}@example.com",
        "role": role
    }
```

## Consequences

### Positive

- ✅ **Clear organization**: API tests separated from unit tests
- ✅ **Contract validation**: Responses verified against OpenAPI spec
- ✅ **Shared fixtures**: Common setup reduces duplication
- ✅ **CI integration**: Different test types run appropriately
- ✅ **Scalable**: Structure supports growing test suite

### Negative

- ⚠️ **Setup overhead**: Requires initial structure and fixtures
- ⚠️ **Dependency**: Contract tests need OpenAPI spec maintained
- ⚠️ **Complexity**: More directories and files to manage

### Neutral

- 📊 **Learning curve**: Team needs to understand structure
- 📊 **Maintenance**: Fixtures need updating as API evolves

## Alternatives Considered

### Alternative 1: All Tests in One Directory

**Description**: Keep all tests in `tests/` without separation.

**Rejected because**:
- ❌ Hard to run API tests in isolation
- ❌ Mixed concerns in conftest.py
- ❌ No clear structure for contract tests
- ❌ Slower test runs

### Alternative 2: Separate Test Package

**Description**: Create a separate `api_tests/` package at project root.

**Rejected because**:
- ❌ Fragments test infrastructure
- ❌ Separate pytest configuration needed
- ❌ Harder to share fixtures
- ⚠️ Might be appropriate for very large projects

### Alternative 3: Schemathesis for Contract Testing

**Description**: Use schemathesis for property-based API testing.

**Considered but deferred**:
- ✅ Powerful property-based testing
- ✅ Auto-generates test cases from spec
- ⚠️ Higher learning curve
- 📊 Can be added later as enhancement

## Related Decisions

- KIT-ADR-0010: OpenAPI Specification Strategy (provides spec for contract tests)
- KIT-ADR-0005: Test Infrastructure Strategy (general testing approach)
- KIT-ADR-0016: Validation Architecture (input validation patterns)

## References

- pytest Documentation: https://docs.pytest.org/
- FastAPI Testing: https://fastapi.tiangolo.com/tutorial/testing/
- openapi-core: https://openapi-core.readthedocs.io/
- Schemathesis: https://schemathesis.readthedocs.io/

## Revision History

- 2025-11-29: Initial decision (Accepted)
  - Established directory structure for API tests
  - Documented fixture patterns and test categories
  - Defined CI integration approach

---

**Template Version**: 1.1.0
**Last Updated**: 2025-11-29
**Project**: agentive-starter-kit
