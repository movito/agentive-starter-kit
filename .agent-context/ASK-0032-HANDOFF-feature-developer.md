# ASK-0032: UV Auto-Detection - Implementation Handoff

**Date**: 2026-02-05
**From**: Planner
**To**: feature-developer
**Task**: delegation/tasks/2-todo/ASK-0032-uv-auto-detection.md
**Status**: Ready for implementation
**Evaluation**: N/A (straightforward enhancement)

---

## Task Summary

Add automatic `uv` detection to the project setup script. When Python 3.13+ is detected and `uv` is available, automatically create a virtual environment with Python 3.12 instead of failing with an error.

## Current Situation

**Problem**: Users with Python 3.13 (increasingly common via Homebrew) hit this error:

```
❌ Python 3.13.7 is not yet supported
   adversarial-workflow requires Python >=3.10,<3.13
   (constraint from aider-chat dependency)

   Options:
   - Use pyenv: pyenv install 3.12 && pyenv local 3.12
   - Use brew:  brew install python@3.12
   - Download:  https://www.python.org/downloads/

   Then run: python3.12 scripts/project setup
```

**Root cause**: `aider-chat` (dependency of `adversarial-workflow`) requires Python <3.13.

**Solution**: Use `uv` to auto-install Python 3.12 and create venv with it.

## Your Mission

Modify `scripts/project` to detect `uv` and use it when Python 3.13+ is detected.

### Phase 1: Write Tests (TDD Red Phase)

Create `tests/test_uv_detection.py` with tests for:
- `detect_uv()` - returns True/False based on `uv` availability
- `create_venv_with_uv()` - creates venv with specified Python version
- Integration: setup uses uv when Python 3.13+ and uv available
- Error handling: graceful failure when uv fails

### Phase 2: Implement Features (TDD Green Phase)

Add to `scripts/project`:
1. `detect_uv()` function
2. `create_venv_with_uv()` function
3. Modify `cmd_setup()` to use uv when appropriate

### Phase 3: Polish (TDD Refactor Phase)

- Clear log messages
- Improved error message when uv not available
- Update README if needed

## Acceptance Criteria (Must Have)

- [ ] **Detection**: `detect_uv()` correctly identifies uv availability
- [ ] **Auto-create**: Python 3.13+ with uv creates 3.12 venv automatically
- [ ] **Fallback**: Python 3.13+ without uv shows improved error (recommending uv)
- [ ] **No regression**: Python 3.10-3.12 behavior unchanged
- [ ] **Tests**: All new tests passing, 80%+ coverage
- [ ] **CI**: All checks pass

## Critical Implementation Details

### 1. UV Detection

```python
import shutil

def detect_uv() -> bool:
    """Check if uv is available on the system."""
    return shutil.which("uv") is not None
```

### 2. UV Venv Creation

```python
def create_venv_with_uv(venv_dir: Path, python_version: str = "3.12") -> bool:
    """Create venv using uv with specified Python version.

    uv will auto-download the Python version if not cached.
    """
    try:
        result = subprocess.run(
            ["uv", "venv", str(venv_dir), "--python", python_version],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"⚠️  uv failed: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"⚠️  uv error: {e}")
        return False
```

### 3. Integration into cmd_setup()

Current flow (lines ~297-322 in `scripts/project`):
```
1. Check Python version
2. If <3.10: fail with "too old"
3. If >=3.13: fail with "not yet supported"
4. If 3.10-3.12: proceed with venv creation
```

New flow:
```
1. Check Python version
2. If <3.10: fail with "too old"
3. If >=3.13:
   a. If uv available: use uv to create 3.12 venv
   b. If uv not available: fail with improved error message
4. If 3.10-3.12: proceed with standard venv creation
```

### 4. Improved Error Message (when uv not available)

```python
if (major, minor) >= (3, 13):
    if detect_uv():
        print(f"⚠️  Python {version_str} detected, using uv to create 3.12 venv...")
        if create_venv_with_uv(venv_dir, "3.12"):
            print("✅ Created venv with Python 3.12 (via uv)")
            # Continue with install...
        else:
            print("❌ uv failed to create venv")
            print("   Try manually: uv venv .venv --python 3.12")
            sys.exit(1)
    else:
        print(f"❌ Python {version_str} is not yet supported")
        print("   adversarial-workflow requires Python >=3.10,<3.13")
        print()
        print("   Recommended: Install uv (auto-manages Python versions)")
        print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("   uv venv .venv --python 3.12")
        print()
        print("   Alternative options:")
        print("   - Use pyenv: pyenv install 3.12 && pyenv local 3.12")
        print("   - Use brew:  brew install python@3.12")
        sys.exit(1)
```

## Resources for Implementation

- **Current setup code**: `scripts/project` lines 290-360
- **ASK-0030** (completed): `delegation/tasks/5-done/ASK-0030-python-version-ceiling.md`
- **uv documentation**: https://docs.astral.sh/uv/
- **Test template**: `tests/test_template.py`

## Time Estimate

2-3 hours total:
- Phase 1 (Tests): 1 hour
- Phase 2 (Implementation): 1 hour
- Phase 3 (Polish): 30 min
- Documentation: 30 min

## Starting Point

1. **Create branch**: `git checkout -b feature/ASK-0032-uv-auto-detection`
2. **Start task**: `./scripts/project start ASK-0032` to move task to in-progress
3. **Read**: `scripts/project` lines 290-360 to understand current flow
3. **Create**: `tests/test_uv_detection.py` with failing tests
4. **Implement**: Add functions to `scripts/project`
5. **Test**: Run `pytest tests/test_uv_detection.py -v`
6. **Verify**: Run `./scripts/ci-check.sh`

## Questions for Planner

If blocked or unclear on:
- How to handle edge cases not covered
- Whether to add CLI flag for specifying Python version
- Documentation updates needed

Report back via updating this handoff file or agent-handoffs.json.

## Success Looks Like

```bash
# User with Python 3.13 and uv installed:
$ python3 scripts/project setup
⚠️  Python 3.13.7 detected, using uv to create 3.12 venv...
✅ Created venv with Python 3.12 (via uv)
✅ Virtual environment exists: /path/to/.venv
📦 Installing dependencies...
✅ Dependencies installed
...

# User with Python 3.13 without uv:
$ python3 scripts/project setup
❌ Python 3.13.7 is not yet supported
   adversarial-workflow requires Python >=3.10,<3.13

   Recommended: Install uv (auto-manages Python versions)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv venv .venv --python 3.12

   Alternative options:
   - Use pyenv: pyenv install 3.12 && pyenv local 3.12
   - Use brew:  brew install python@3.12

# User with Python 3.12 (no change):
$ python3 scripts/project setup
✅ Python 3.12.0
📦 Creating virtual environment...
...
```

## Notes

- `uv venv --python 3.12` will auto-download Python 3.12 if not cached
- This is a non-breaking change - existing users with 3.10-3.12 see no difference
- When aider-chat adds 3.13 support, this code becomes a no-op (graceful)

---

**Task File**: `delegation/tasks/2-todo/ASK-0032-uv-auto-detection.md`
**Handoff Date**: 2026-02-05
**Coordinator**: Planner
