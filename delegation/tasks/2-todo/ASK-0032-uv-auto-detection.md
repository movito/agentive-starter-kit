# ASK-0032: Add UV Auto-Detection for Python Version Management

**Status**: Todo
**Priority**: High
**Assigned To**: feature-developer
**Estimated Effort**: 2-3 hours
**Created**: 2026-02-05
**Target Completion**: 2026-02-07
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent Task**: ASK-0030 (Python Version Ceiling Check)
**Depends On**: None
**Blocks**: None
**Related**: ASK-0030, ASK-0031

## Overview

Users with Python 3.13+ cannot run `./scripts/project setup` because `aider-chat` (dependency of `adversarial-workflow`) requires `Python <3.13`. Currently, setup fails with an error asking users to manually install Python 3.12.

**The problem**: macOS users with Homebrew increasingly have Python 3.13 as their default. Manual workarounds create friction for new project setups.

**The solution**: Detect if `uv` is installed and use it to automatically create a venv with Python 3.12, bypassing the system Python entirely.

**Context**: [uv](https://github.com/astral-sh/uv) is a modern Python package manager that can auto-install any Python version. It's becoming standard in the Python ecosystem.

**Related Work**:
- ASK-0030 added the Python version ceiling check
- ASK-0031 improved venv activation UX

## Requirements

### Functional Requirements
1. Detect if `uv` is available on the system (via `which uv` or `shutil.which`)
2. If Python 3.13+ detected AND `uv` available: auto-create venv with Python 3.12
3. If Python 3.13+ detected AND `uv` NOT available: show improved error message recommending `uv`
4. If Python 3.10-3.12: proceed with existing behavior (no change)
5. Log which method was used for venv creation

### Non-Functional Requirements
- [ ] Performance: No additional latency for compatible Python versions
- [ ] Reliability: Graceful fallback if uv fails
- [ ] Security: No execution of untrusted code
- [ ] Maintainability: Clear separation of uv vs standard venv creation

## TDD Workflow (Mandatory)

**Test-Driven Development Approach**:

1. **Before coding**: Create `tests/test_uv_detection.py`
2. **Red**: Write failing tests for uv detection and venv creation
3. **Green**: Implement minimum code until tests pass
4. **Refactor**: Improve code while keeping tests green
5. **Commit**: Pre-commit hook runs tests automatically

**TDD Benefits for this task**:
- Ensures uv detection works across platforms
- Catches edge cases (uv installed but broken, etc.)
- Documents expected behavior for future maintainers

### Test Requirements
- [ ] Unit tests for `detect_uv()` function
- [ ] Unit tests for `create_venv_with_uv()` function
- [ ] Integration test for full setup flow with mocked uv
- [ ] Error handling tests for uv failure scenarios
- [ ] Edge case tests: uv in PATH but not executable, uv returns error

**Test files to create**:
- `tests/test_uv_detection.py` - Main test suite

## Test Coverage Requirements

**Coverage Targets**:
- [ ] New code: **80%+ line coverage** (mandatory)
- [ ] Overall coverage: **≥53%** (maintain baseline)
- [ ] Critical paths: **100% coverage** (mandatory)
- [ ] Error paths: **80%+ coverage**

**Critical Paths** (require 100% coverage):
1. uv detection logic
2. Python version check decision tree
3. Error message generation

## Implementation Plan

### Files to Modify

1. `scripts/project` - Main setup script
   - Function: `cmd_setup()`
   - Change: Add uv detection and conditional venv creation
   - Lines: ~297-360 (version check section)

### Files to Create

1. `tests/test_uv_detection.py` - Test suite
   - Purpose: Test uv detection and venv creation
   - Contains: `test_detect_uv_*`, `test_create_venv_*`
   - Estimated tests: ~10-15 tests

### Approach

**Step 1: Write Tests (1 hour)**

```python
# tests/test_uv_detection.py
def test_detect_uv_when_installed(monkeypatch):
    """Should return True when uv is in PATH."""
    monkeypatch.setattr(shutil, 'which', lambda x: '/usr/local/bin/uv' if x == 'uv' else None)
    assert detect_uv() is True

def test_detect_uv_when_not_installed(monkeypatch):
    """Should return False when uv is not in PATH."""
    monkeypatch.setattr(shutil, 'which', lambda x: None)
    assert detect_uv() is False

def test_setup_uses_uv_for_python313(monkeypatch):
    """Python 3.13+ with uv should auto-create 3.12 venv."""
    # ... test implementation
```

**Step 2: Implement Detection Logic (1 hour)**

```python
def detect_uv() -> bool:
    """Check if uv is available on the system."""
    return shutil.which("uv") is not None

def create_venv_with_uv(venv_dir: Path, python_version: str = "3.12") -> bool:
    """Create venv using uv with specified Python version."""
    try:
        result = subprocess.run(
            ["uv", "venv", str(venv_dir), "--python", python_version],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception:
        return False
```

**Step 3: Integrate into Setup Flow (30 min)**

Modify `cmd_setup()` to use the new functions.

**Step 4: Update Error Messages (30 min)**

When uv is not available, suggest it as the primary solution.

## Acceptance Criteria

### Must Have
- [ ] `uv` detection works correctly (True when installed, False otherwise)
- [ ] Python 3.13+ with `uv`: automatically creates 3.12 venv
- [ ] Python 3.13+ without `uv`: shows clear error with `uv` as recommended solution
- [ ] Python 3.10-3.12: no behavior change
- [ ] All tests passing
- [ ] Coverage targets met

### Should Have
- [ ] Clear log messages showing which venv method was used
- [ ] Error message includes `uv` installation command

### Nice to Have
- [ ] Detect if uv has Python 3.12 already cached
- [ ] Support user-specified Python version via flag

## Success Metrics

### Quantitative
- Test pass rate: 100%
- Coverage: 80%+ for new code
- Setup success rate: 100% for users with `uv` installed
- LOC added: ~50-80 lines

### Qualitative
- Setup "just works" for users with uv
- Error messages are actionable
- Code is easy to maintain

## Risks & Mitigations

### Risk 1: uv API changes
**Likelihood**: Low
**Impact**: Medium
**Mitigation**:
- Use simple, stable uv commands (`uv venv --python`)
- Add version check for uv if needed

### Risk 2: uv fails to download Python
**Likelihood**: Low
**Impact**: Medium
**Mitigation**:
- Graceful error handling with clear message
- Fallback to manual installation instructions

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| TDD: Write failing tests | 1 hour | [ ] |
| TDD: Implement features | 1 hour | [ ] |
| Integration & testing | 30 min | [ ] |
| Documentation | 30 min | [ ] |
| **Total** | **2-3 hours** | [ ] |

## References

### Testing & Development
- **TDD Template**: `tests/test_template.py`
- **Commit Protocol**: `.agent-context/workflows/COMMIT-PROTOCOL.md`
- **Pre-commit Config**: `.pre-commit-config.yaml`

### Related
- **ASK-0030**: Python version ceiling check (completed)
- **uv documentation**: https://github.com/astral-sh/uv
- **aider-chat**: https://github.com/Aider-AI/aider (Python <3.13 constraint source)

## Notes

- The `aider-chat` Python 3.13 constraint may be lifted eventually
- When that happens, this code becomes a no-op (graceful degradation)
- `uv` is recommended by the broader Python community (PEP 723)
- This approach aligns with modern Python tooling trends

---

**Template Version**: 1.0.0
**Created**: 2026-02-05
