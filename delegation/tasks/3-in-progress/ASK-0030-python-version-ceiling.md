# ASK-0030: Add Python Version Ceiling Check

**Status**: In Progress
**Priority**: High
**Assigned To**: feature-developer
**Estimated Effort**: 1 hour
**Created**: 2026-02-01
**Source**: User report - Python 3.13 incompatibility with aider-chat

## Problem Statement

The `./scripts/project setup` command checks for Python `>=3.9` but doesn't check for an upper bound. The `aider-chat` package (dependency of `adversarial-workflow`) requires `Python >=3.10,<3.13`.

**Current behavior:**
```
✅ Python 3.13.7

📦 Creating virtual environment...
✅ Created: /path/to/.venv

📦 Installing dependencies...
❌ Failed to install dependencies:
ERROR: No matching distribution found for aider-chat>=0.86.0
```

Users get a cryptic pip error instead of a clear version warning upfront.

**Expected behavior:**
```
❌ Python 3.13.7 is not supported
   adversarial-workflow requires Python >=3.10,<3.13

   Options:
   - Use pyenv to install Python 3.12: pyenv install 3.12
   - Use Python 3.12 directly: python3.12 -m venv .venv
```

## Requirements

### Must Have

- [x] Update `scripts/project` setup command to check Python version ceiling
- [x] Check for `<3.13` (aider-chat constraint)
- [x] Show clear error message with remediation options
- [x] Fail fast before creating venv (don't waste user time)

### Should Have

- [x] Update `pyproject.toml` to add `requires-python = ">=3.10,<3.13"`
- [ ] Add version check to `./scripts/verify-setup.sh`

### Nice to Have

- [ ] Detect pyenv and suggest version switch
- [ ] Offer to create venv with specific Python version if available

## Evaluation Feedback (Round 1)

**Verdict**: NEEDS_REVISION

**Concerns Addressed**:
1. ✅ Python 3.13 handling - The code uses `>= (3, 13)` which handles 3.13, 3.14, etc.
2. ✅ Alternative tools - Error messages include pyenv AND brew options
3. ✅ Impact on existing code - This is an additive check; existing setups continue to work

**Clarifications**:
- Users without pyenv/brew can manually download Python from python.org
- When aider-chat adds 3.13 support, update the ceiling check and pyproject.toml
- No breaking changes to existing code; this adds a pre-flight check only

## Implementation

### 1. Update scripts/project setup command

In `cmd_setup()`, update the Python version check:

```python
def cmd_setup(args):
    """Create virtual environment and install dependencies."""
    import sys

    # Check Python version bounds
    major, minor = sys.version_info[:2]
    version_str = f"{major}.{minor}.{sys.version_info[2]}"

    # Lower bound
    if (major, minor) < (3, 10):
        print(f"❌ Python {version_str} is too old")
        print("   Minimum required: Python 3.10")
        print()
        print("   Install a newer Python version:")
        print("   - pyenv: pyenv install 3.12")
        print("   - brew:  brew install python@3.12")
        sys.exit(1)

    # Upper bound (aider-chat constraint: Python <3.13)
    if (major, minor) >= (3, 13):
        print(f"❌ Python {version_str} is not yet supported")
        print("   adversarial-workflow requires Python >=3.10,<3.13")
        print("   (constraint from aider-chat dependency)")
        print()
        print("   Options:")
        print("   - Use pyenv: pyenv install 3.12 && pyenv local 3.12")
        print("   - Use brew:  brew install python@3.12")
        print("   - Download:  https://www.python.org/downloads/")
        print()
        print("   Then run: python3.12 scripts/project setup")
        sys.exit(1)

    print(f"✅ Python {version_str}")
    # ... rest of setup
```

### 2. Update pyproject.toml

```toml
[project]
requires-python = ">=3.10,<3.13"
```

This ensures pip itself will reject installation on incompatible Python versions.

### 3. Update verify-setup.sh (optional)

Add version ceiling check to the verification script.

## Acceptance Criteria

1. Running `./scripts/project setup` on Python 3.13+ shows clear error with options
2. Running on Python <3.10 shows clear error with upgrade instructions
3. Running on Python 3.10-3.12 proceeds normally
4. `pyproject.toml` specifies version constraints
5. Error messages include actionable remediation steps

## Testing

### Manual Testing

```bash
# Test with Python 3.13 (should fail with clear message)
python3.13 scripts/project setup

# Test with Python 3.12 (should work)
python3.12 scripts/project setup

# Test with Python 3.9 (should fail - too old)
python3.9 scripts/project setup
```

### Unit Tests

Add to `tests/test_project_script.py`:

```python
def test_python_version_ceiling_error(capsys, monkeypatch):
    """Python 3.13+ should show clear error."""
    monkeypatch.setattr(sys, 'version_info', (3, 13, 0))
    # Test error message contains expected text
```

## Related

- **ASK-0028**: Project setup command (original implementation)
- **adversarial-workflow**: https://github.com/movito/adversarial-workflow
- **aider-chat**: https://github.com/paul-gauthier/aider (Python <3.13 constraint)

## Notes

- The Python 3.13 constraint comes from `aider-chat`, not `adversarial-workflow` directly
- When aider-chat adds Python 3.13 support, we can update the ceiling
- The error message should be helpful, not just "version not supported"
