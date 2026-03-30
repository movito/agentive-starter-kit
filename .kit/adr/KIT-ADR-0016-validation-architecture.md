# KIT-ADR-0016: Validation Architecture

**Status**: Accepted

**Date**: 2025-11-29

**Deciders**: planner, User

## Context

### Problem Statement

Data validation in multi-step workflows presents a fundamental tension: strict validation at object creation prevents working with incomplete data, while lenient validation leads to invalid data reaching operations. We need a pattern that allows:
- Working with partially complete data during editing
- Strict validation before critical operations
- Clear error messages with appropriate context
- Type safety without excessive ceremony

### Forces at Play

**Technical Requirements:**
- Objects must be type-safe when created
- Operations (sync, API calls) require complete, valid data
- Editing workflows need partial data support
- Validation errors must be actionable

**Constraints:**
- Python type system has limits (Optional vs required)
- Pydantic validates at construction by default
- Different operations have different validation requirements
- Error messages need context (what operation, what's missing)

**Assumptions:**
- Data models will be reused across operations
- Users will edit data incrementally
- Some operations are more strict than others
- Validation logic should be testable in isolation

## Decision

We will adopt a **two-tier validation architecture** that separates type safety (construction) from comprehensive validation (operation-specific).

### Core Principles

1. **Tier 1 - Construction**: Ensure type safety when objects are created
2. **Tier 2 - Operation**: Validate comprehensively before specific operations
3. **Explicit validation**: Call `.validate_for_X()` before operations
4. **Context-rich errors**: Validation errors include operation context

### Two-Tier Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Object Lifecycle                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Creation ──► Tier 1 (Type Safety)                  │
│     │              ↓                                 │
│     │         Object exists (may be partial)        │
│     │              │                                 │
│  Editing ◄────────┘                                 │
│     │                                                │
│  Operation ──► Tier 2 (Comprehensive)               │
│                    ↓                                 │
│              Pass: Proceed                          │
│              Fail: Actionable errors                │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Implementation Details

**Tier 1: Type Safety at Construction**

Uses Pydantic's default validation with Optional fields for partial data:

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Task(BaseModel):
    """Task with Tier 1 type safety."""

    # Required fields - must be provided at construction
    id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)

    # Optional fields - can be None during editing
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        # Strict mode for better type safety
        strict = True
```

**Tier 2: Comprehensive Validation for Operations**

Named validation methods that check everything needed for a specific operation:

```python
class Task(BaseModel):
    # ... Tier 1 fields above ...

    def validate_for_linear_sync(self) -> list[ValidationError]:
        """
        Tier 2: Validate for Linear sync operation.

        Returns list of errors (empty = valid).
        """
        errors = []

        # Status is required for sync
        if not self.status:
            errors.append(ValidationError(
                field="status",
                message="Status is required for Linear sync",
                suggestion="Set status to one of: Backlog, Todo, In Progress, Done"
            ))
        elif self.status not in VALID_LINEAR_STATUSES:
            errors.append(ValidationError(
                field="status",
                message=f"Invalid status '{self.status}' for Linear",
                suggestion=f"Valid values: {', '.join(VALID_LINEAR_STATUSES)}"
            ))

        # Priority should be set
        if not self.priority:
            errors.append(ValidationError(
                field="priority",
                message="Priority is recommended for Linear sync",
                severity="warning"  # Not blocking
            ))

        return errors

    def validate_for_api_response(self) -> list[ValidationError]:
        """
        Tier 2: Validate for API response.

        API responses can have different requirements than sync.
        """
        errors = []

        # API allows null status (will be inferred)
        # But requires created_at
        if not self.created_at:
            errors.append(ValidationError(
                field="created_at",
                message="Timestamp required for API response"
            ))

        return errors
```

**ValidationError Structure**

```python
from dataclasses import dataclass
from typing import Optional, Literal

@dataclass
class ValidationError:
    """Structured validation error with context."""

    field: str
    message: str
    suggestion: Optional[str] = None
    severity: Literal["error", "warning"] = "error"

    def __str__(self) -> str:
        base = f"{self.field}: {self.message}"
        if self.suggestion:
            base += f" ({self.suggestion})"
        return base
```

**Usage Pattern**

```python
# Tier 1: Create object (type-safe, partial OK)
task = Task(id="ASK-0018", title="Validation ADR")
# status is None - that's fine for now

# Work with partial object
task.title = "Updated Title"
task.status = "In Progress"

# Tier 2: Validate before operation
errors = task.validate_for_linear_sync()
if errors:
    for error in errors:
        if error.severity == "error":
            print(f"ERROR: {error}")
        else:
            print(f"WARNING: {error}")
    # Handle errors appropriately
else:
    # Proceed with sync
    linear_client.sync_task(task)
```

### When to Use Each Tier

| Scenario | Tier 1 | Tier 2 | Notes |
|----------|--------|--------|-------|
| Creating new object | ✅ | ❌ | Just type safety |
| Loading from file | ✅ | ❌ | May be incomplete |
| Editing in UI | ✅ | ❌ | Allow partial state |
| Saving draft | ✅ | ❌ | Preserve work |
| Syncing to Linear | ✅ | ✅ | Must be complete |
| API response | ✅ | ✅ | Must meet contract |
| Batch processing | ✅ | ✅ | All items must validate |

### Error Handling Patterns

**Pattern 1: Fail Fast (Operations)**

```python
def sync_to_linear(task: Task) -> None:
    """Sync task to Linear - requires full validation."""
    errors = task.validate_for_linear_sync()
    blocking_errors = [e for e in errors if e.severity == "error"]

    if blocking_errors:
        raise ValidationException(
            operation="linear_sync",
            errors=blocking_errors
        )

    # Proceed with sync
    _do_sync(task)
```

**Pattern 2: Collect and Report (Batch)**

```python
def sync_all_tasks(tasks: list[Task]) -> SyncResult:
    """Sync multiple tasks, collecting errors."""
    results = SyncResult()

    for task in tasks:
        errors = task.validate_for_linear_sync()
        if errors:
            results.add_failure(task.id, errors)
        else:
            _do_sync(task)
            results.add_success(task.id)

    return results
```

**Pattern 3: Warn and Continue (Non-blocking)**

```python
def prepare_task_report(task: Task) -> Report:
    """Generate report with validation warnings."""
    errors = task.validate_for_api_response()
    warnings = [e for e in errors if e.severity == "warning"]

    report = generate_report(task)
    report.warnings = warnings  # Include but don't block

    return report
```

### Pydantic v2 Integration

For projects using Pydantic v2:

```python
from pydantic import BaseModel, model_validator

class Task(BaseModel):
    id: str
    title: str
    status: str | None = None

    @model_validator(mode='after')
    def tier1_validation(self) -> 'Task':
        """Tier 1: Basic invariants that must always hold."""
        if self.id and not self.id.startswith(('ASK-', 'TASK-')):
            # This is a type-level constraint, not operation-specific
            raise ValueError(f"Invalid ID format: {self.id}")
        return self

    def validate_for_linear_sync(self) -> list[ValidationError]:
        """Tier 2: Linear-specific validation."""
        # Operation-specific validation here
        ...
```

## Consequences

### Positive

- ✅ **Better UX**: Users can work with incomplete data during editing
- ✅ **Clearer errors**: Operation-specific messages with suggestions
- ✅ **Flexibility**: Different operations have different requirements
- ✅ **Testability**: Validation methods can be tested in isolation
- ✅ **Type safety**: Pydantic ensures basic type correctness

### Negative

- ⚠️ **Discipline required**: Developers must call validate before operations
- ⚠️ **Code duplication**: Similar validation across methods
- ⚠️ **Discovery**: Must know which validate method to call

### Neutral

- 📊 **API surface**: More methods per model
- 📊 **Documentation**: Must document when to validate

## Alternatives Considered

### Alternative 1: Strict Validation at Construction

**Description**: Require all fields and validate everything at object creation.

**Rejected because**:
- ❌ Can't create partial objects during editing
- ❌ Loading incomplete data from files fails
- ❌ All-or-nothing approach hurts UX
- ❌ No context-specific error messages

### Alternative 2: No Construction Validation

**Description**: Accept any data at construction, validate only before operations.

**Rejected because**:
- ❌ Type errors caught late
- ❌ Invalid data can propagate
- ❌ Harder to reason about object state
- ❌ Misses benefits of type safety

### Alternative 3: Validation Decorators

**Description**: Use decorators to automatically validate before method calls.

**Rejected because**:
- ❌ Magic behavior - not obvious when validation runs
- ❌ Harder to handle errors explicitly
- ❌ Less control over validation flow
- ⚠️ Could be added later as enhancement

### Alternative 4: Separate DTOs per Operation

**Description**: Create different model classes for different operations.

**Rejected because**:
- ❌ Class explosion (TaskDraft, TaskForSync, TaskForApi, etc.)
- ❌ Conversion overhead between types
- ❌ Harder to maintain consistency
- ⚠️ Sometimes appropriate for very different shapes

## Testing Strategy

### Unit Testing Validation Methods

```python
def test_validate_for_linear_sync_missing_status():
    """Tier 2 validation should catch missing status."""
    task = Task(id="ASK-001", title="Test Task")
    # status is None

    errors = task.validate_for_linear_sync()

    assert len(errors) == 1
    assert errors[0].field == "status"
    assert "required" in errors[0].message.lower()

def test_validate_for_linear_sync_valid():
    """Valid task should pass Tier 2 validation."""
    task = Task(
        id="ASK-001",
        title="Test Task",
        status="In Progress",
        priority="high"
    )

    errors = task.validate_for_linear_sync()

    assert len(errors) == 0
```

### Integration Testing

```python
def test_sync_fails_with_invalid_task(linear_client):
    """Sync should fail for invalid tasks."""
    task = Task(id="ASK-001", title="Test")  # No status

    with pytest.raises(ValidationException) as exc:
        sync_to_linear(task)

    assert "status" in str(exc.value)
```

## Related Decisions

- KIT-ADR-0012: Task Status Linear Alignment (uses this pattern)
- KIT-ADR-0010: OpenAPI Specification Strategy (API validation)

## References

- Pydantic v2 Documentation: https://docs.pydantic.dev/
- Parse, don't validate: https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
- Domain Driven Design - Value Objects

## Revision History

- 2025-11-29: Initial decision (Accepted)
  - Documented two-tier validation pattern
  - Established validation error structure
  - Defined testing strategy

---

**Template Version**: 1.1.0
**Last Updated**: 2025-11-29
**Project**: agentive-starter-kit
