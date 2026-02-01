# ASK-0031: Improve Virtual Environment Activation UX

**Status**: In Progress
**Priority**: Medium
**Assigned To**: feature-developer
**Estimated Effort**: 2 hours
**Created**: 2026-02-01
**Source**: User feedback - users forget to activate venv after setup

## Problem Statement

After running `./scripts/project setup`, users frequently forget to activate the virtual environment. The current output is confusing:

**Current output:**
```
source .venv/bin/activate    <-- This looks like output, not an instruction
✅ Python 3.12.0

📦 Creating virtual environment...
✅ Created: /path/to/.venv

📦 Installing dependencies...
✅ Installed successfully
...
```

The `source .venv/bin/activate` at the top is meant to be a "run this next" instruction, but it's displayed without context and gets lost in the output.

**Expected behavior:**
Clear "next steps" section at the end with copy-pasteable command.

## Requirements

### Must Have

- [ ] Move activation instruction to END of setup output (not beginning)
- [ ] Add clear visual separator and "Next Steps" header
- [ ] Make the command copy-pasteable (no extra formatting)
- [ ] Detect if already in venv and skip the instruction

### Should Have

- [ ] Add activation reminder to onboarding agent flow
- [ ] Detect shell type and show correct command (bash/zsh vs fish)

### Nice to Have

- [ ] Auto-copy command to clipboard (with user permission)
- [ ] Add `./scripts/project activate` wrapper that prints the command

## Evaluation Feedback (Round 1)

**Verdict**: NEEDS_REVISION

**Concerns Addressed**:
1. ✅ Error handling - The "Next Steps" section only appears AFTER successful setup; errors are already handled upstream
2. ✅ Shell fallback - Default to bash/zsh syntax; it works on most systems including when SHELL is unset
3. ✅ Automated tests - Test stubs provided in Testing section

**Clarifications**:
- Error handling for venv creation already exists in cmd_setup(); this task only modifies success output
- Shell detection is a "Should Have" enhancement, not blocking core functionality
- Documentation updates are not needed; this is internal script output only

## Implementation

### 1. Update scripts/project setup command

Replace the current output with a clear "Next Steps" section at the end:

```python
def cmd_setup(args):
    # ... existing setup code ...

    # At the end, after successful setup:
    print()
    print("=" * 50)
    print("✅ Setup complete!")
    print("=" * 50)
    print()

    # Check if already in venv
    if os.environ.get("VIRTUAL_ENV"):
        print("You're already in a virtual environment.")
        print("Run: pip install -e '.[dev]'  # if needed")
    else:
        print("📋 Next step - activate the virtual environment:")
        print()
        print("    source .venv/bin/activate")
        print()
        print("Then you can run:")
        print("    pytest tests/ -v          # Run tests")
        print("    adversarial --help        # Evaluation CLI")
        print("    ./scripts/project help    # Project commands")
```

### 2. Update onboarding agent

Add venv activation reminder to `.claude/agents/onboarding.md`:

```markdown
## Phase 3: Environment Setup

After running `./scripts/project setup`:

**IMPORTANT**: Remind the user to activate the virtual environment:

```bash
source .venv/bin/activate
```

Verify activation by checking:
- Shell prompt shows `(.venv)` prefix
- `which python` points to `.venv/bin/python`

If the user forgets, they'll see "command not found" errors for project tools.
```

### 3. Detect shell type (optional enhancement)

```python
def get_activate_command():
    """Return shell-appropriate activate command."""
    shell = os.environ.get("SHELL", "")
    if "fish" in shell:
        return "source .venv/bin/activate.fish"
    elif "csh" in shell or "tcsh" in shell:
        return "source .venv/bin/activate.csh"
    else:
        # Default: works for bash, zsh, sh, and most POSIX shells
        return "source .venv/bin/activate"
```

**Note**: The default `source .venv/bin/activate` works for bash, zsh, sh, dash, and other POSIX-compatible shells. This covers 95%+ of users.

## Acceptance Criteria

1. Setup command shows "Next Steps" section at END of output
2. Activation command is clearly labeled and copy-pasteable
3. If already in venv, shows appropriate message instead
4. Onboarding agent includes activation reminder
5. No confusing output at the beginning of setup

## Testing

### Manual Testing

```bash
# Test outside venv
deactivate 2>/dev/null
./scripts/project setup
# Verify: "Next Steps" section appears at end with activate command

# Test inside venv
source .venv/bin/activate
./scripts/project setup
# Verify: Shows "already in virtual environment" message
```

### Unit Tests

Add to `tests/test_project_script.py`:

```python
def test_setup_shows_next_steps(capsys, tmp_path, monkeypatch):
    """Setup should show clear next steps at end."""
    # Mock successful setup
    # Verify output contains "Next step" and "source .venv/bin/activate"

def test_setup_detects_active_venv(capsys, monkeypatch):
    """Setup should detect if already in venv."""
    monkeypatch.setenv("VIRTUAL_ENV", "/some/path")
    # Verify output mentions "already in a virtual environment"
```

## Related

- **ASK-0028**: Project setup command (original implementation)
- **ASK-0030**: Python version ceiling check

## Notes

- The key insight is that instructions should come AFTER the work is done
- Users scan output top-to-bottom; important next steps at the end are more visible
- Detecting venv status prevents confusing "activate when already active" scenarios
