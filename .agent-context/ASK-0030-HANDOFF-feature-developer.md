# ASK-0030 Handoff: Python Version Ceiling Check

**Task**: `delegation/tasks/2-todo/ASK-0030-python-version-ceiling.md`
**Prepared by**: Planner
**Date**: 2026-02-01
**Evaluation Rounds**: 1 (GPT-4o) - concerns addressed in task file

## Context

Users on Python 3.13+ encounter cryptic pip errors during setup because `aider-chat` (dependency of `adversarial-workflow`) requires Python <3.13. This task adds an upfront version check with clear error messages.

## Implementation Sequence

### Phase 1: Update scripts/project (Must Have)

1. **Locate `cmd_setup()` function** in `scripts/project`
2. **Add version ceiling check** before venv creation:
   - Check `sys.version_info >= (3, 13)`
   - Print clear error with options (pyenv, brew, python.org)
   - Exit with code 1
3. **Update lower bound** from 3.9 to 3.10 (align with aider-chat)

### Phase 2: Update pyproject.toml (Should Have)

4. **Add `requires-python`** constraint:
   ```toml
   [project]
   requires-python = ">=3.10,<3.13"
   ```

### Phase 3: Testing

5. **Unit tests** in `tests/test_project_script.py`:
   - Mock `sys.version_info` to test both bounds
   - Verify error messages contain expected text

## Files to Modify

| File | Change |
|------|--------|
| `scripts/project` | Add version ceiling check in `cmd_setup()` |
| `pyproject.toml` | Add `requires-python = ">=3.10,<3.13"` |
| `tests/test_project_script.py` | Add version check tests |

## Key Technical Details

### Version Check Logic
```python
major, minor = sys.version_info[:2]
if (major, minor) < (3, 10):
    # Too old
if (major, minor) >= (3, 13):
    # Too new (aider-chat constraint)
```

### Error Message Requirements
- Show exact version detected
- Explain the constraint source (aider-chat)
- Provide 3 options: pyenv, brew, python.org
- Include command to run with correct Python

## Success Criteria

1. `python3.13 scripts/project setup` shows clear error before venv creation
2. `python3.9 scripts/project setup` shows "too old" error
3. `python3.12 scripts/project setup` proceeds normally
4. `pyproject.toml` has version constraint
5. All tests pass

## Commands to Run

```bash
# Start task
./scripts/project start ASK-0030

# Test the changes (if you have multiple Python versions)
python3.13 scripts/project setup  # Should fail with clear message
python3.12 scripts/project setup  # Should work

# Run tests
pytest tests/test_project_script.py -v -k version

# CI check
./scripts/ci-check.sh
```

---

Ready for implementation by feature-developer agent.
