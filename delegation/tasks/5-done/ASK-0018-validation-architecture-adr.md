# ASK-0018: Validation Architecture ADR

**Status**: Done
**Priority**: low
**Assigned To**: planner
**Estimated Effort**: 2-3 hours
**Created**: 2025-11-28

## Related Tasks

**Parent Task**: None (ADR Migration - Tier 3: API & Quality)
**Depends On**: None
**Blocks**: None
**Related**: ASK-0015 (OpenAPI Specification)

## Overview

Document the Validation Architecture for the agentive-starter-kit. This ADR establishes a two-tier validation pattern: type safety at construction vs comprehensive validation on demand.

**Why Valuable**: Enables better UX by separating "can this object exist?" from "is this object valid for this operation?". Allows working with partially valid data during editing.

## Key Concepts to Document

### Two-Tier Validation

```
Tier 1: Construction (Type Safety)
    - Runs automatically
    - Catches type errors
    - Allows partially valid objects

Tier 2: Comprehensive (Explicit)
    - Runs on demand (.validate())
    - Full business rule validation
    - Required before operations
```

### Example Pattern

```python
from pydantic import BaseModel
from typing import Optional

class Task(BaseModel):
    """Tier 1: Type safety at construction"""
    id: str
    title: str
    status: Optional[str] = None  # Can be None during editing

    def validate_for_sync(self) -> list[str]:
        """Tier 2: Comprehensive validation for Linear sync"""
        errors = []
        if not self.status:
            errors.append("Status required for sync")
        if self.status and self.status not in VALID_STATUSES:
            errors.append(f"Invalid status: {self.status}")
        return errors
```

### When to Use Each Tier

| Scenario | Tier 1 | Tier 2 |
|----------|--------|--------|
| Creating object | ✅ | ❌ |
| Editing in UI | ✅ | ❌ |
| Saving draft | ✅ | ❌ |
| Syncing to Linear | ✅ | ✅ |
| API response | ✅ | ✅ |

### Benefits

1. **Better UX** - Don't fail during editing
2. **Clearer errors** - Context-specific validation messages
3. **Flexibility** - Work with incomplete data
4. **Testability** - Validate in isolation

## Acceptance Criteria

### Must Have

- [ ] ADR created following project template
- [ ] Documents two-tier pattern
- [ ] Shows Pydantic example
- [ ] Explains tier selection criteria
- [ ] Lists benefits of separation

### Should Have

- [ ] Error message patterns
- [ ] Testing strategies
- [ ] Integration with API responses

## Notes

- This pattern is useful for any data model
- Pydantic v2 recommended for performance
- Consider attrs as alternative to Pydantic

---

**Template Version**: 1.0.0
**Created**: 2025-11-28
