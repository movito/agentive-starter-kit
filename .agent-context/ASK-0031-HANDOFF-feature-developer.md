# ASK-0031 Handoff: Virtual Environment Activation UX

**Task**: `delegation/tasks/2-todo/ASK-0031-venv-activation-ux.md`
**Prepared by**: Planner
**Date**: 2026-02-01
**Evaluation Rounds**: 1 (GPT-4o) - concerns addressed in task file

## Context

Users forget to activate the virtual environment after setup because the activation instruction appears at the beginning of output and gets lost. This task moves the instruction to a clear "Next Steps" section at the end.

## Implementation Sequence

### Phase 1: Update scripts/project (Must Have)

1. **Locate success output** in `cmd_setup()` function
2. **Remove** any activation hint from beginning of output
3. **Add "Next Steps" section** at the END:
   - Visual separator (`=` line)
   - "Setup complete!" message
   - Check for existing venv activation
   - Show `source .venv/bin/activate` command
   - List useful next commands

### Phase 2: Shell Detection (Should Have)

4. **Add `get_activate_command()` helper**:
   - Detect fish shell → `activate.fish`
   - Detect csh/tcsh → `activate.csh`
   - Default → `activate` (bash/zsh/sh)

### Phase 3: Update Onboarding (Should Have)

5. **Update `.claude/agents/onboarding.md`**:
   - Add venv activation reminder to Phase 3

### Phase 4: Testing

6. **Add tests** to `tests/test_project_script.py`:
   - Test "Next Steps" appears in output
   - Test venv detection skips activation hint

## Files to Modify

| File | Change |
|------|--------|
| `scripts/project` | Update `cmd_setup()` output, add shell detection |
| `.claude/agents/onboarding.md` | Add activation reminder |
| `tests/test_project_script.py` | Add UX tests |

## Key Technical Details

### Output Format
```
==================================================
✅ Setup complete!
==================================================

📋 Next step - activate the virtual environment:

    source .venv/bin/activate

Then you can run:
    pytest tests/ -v          # Run tests
    adversarial --help        # Evaluation CLI
    ./scripts/project help    # Project commands
```

### Venv Detection
```python
if os.environ.get("VIRTUAL_ENV"):
    # Already in venv - show different message
```

### Shell Detection (Enhancement)
```python
shell = os.environ.get("SHELL", "")
if "fish" in shell:
    return "source .venv/bin/activate.fish"
# etc.
```

## Success Criteria

1. "Next Steps" section appears at END of setup output
2. Activation command is clearly labeled and indented
3. Already-in-venv case shows appropriate message
4. Onboarding agent includes activation reminder
5. All tests pass

## Commands to Run

```bash
# Start task
./scripts/project start ASK-0031

# Test outside venv
deactivate 2>/dev/null
./scripts/project setup
# Verify: "Next Steps" at end

# Test inside venv
source .venv/bin/activate
./scripts/project setup
# Verify: "already in virtual environment" message

# Run tests
pytest tests/test_project_script.py -v

# CI check
./scripts/ci-check.sh
```

---

Ready for implementation by feature-developer agent.
