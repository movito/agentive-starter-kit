# ASK-0028: Add Project Setup Command - Implementation Handoff

**Date**: 2025-02-01
**From**: Planner
**To**: feature-developer
**Task**: delegation/tasks/2-todo/ASK-0028-venv-setup-command.md
**Status**: Ready for implementation
**Evaluation**: 2 rounds, remaining concerns addressed or out-of-scope

---

## Task Summary

Add a `./scripts/project setup` command that creates a Python virtual environment, installs all dependencies, and configures pre-commit hooks. This addresses the root cause of agents failing with "externally-managed-environment" errors when trying to pip install on macOS.

## Current Situation

New projects cloned from the starter kit have no virtual environment:
- macOS Homebrew Python blocks system-wide pip installs
- Agents try `pip install gql` and fail
- Dependencies in `pyproject.toml` aren't available
- No automated setup process exists

Related fix already merged: `sync_tasks_to_linear.py` now gracefully handles missing gql (tests skip instead of failing during collection).

## Your Mission

### Phase 1: Implement `cmd_setup()` in `scripts/project`

Add the setup command handler following the pattern in the task specification. Key features:
- Python 3.9+ version check
- Create `.venv/` directory
- Install deps with `pip install -e ".[dev]"`
- Install pre-commit hooks (if available)
- Handle `--force` flag for recreation
- Corrupted venv detection

### Phase 2: Integrate with Help

Update the help text and command routing:
```python
# In the command dispatch section
elif cmd == "setup":
    cmd_setup(args[1:])
```

Update help output to include:
```
Setup:
  setup [--force]        Create venv and install dependencies
```

### Phase 3: Documentation Updates

Update these files:
1. `README.md` - Add setup step to Quick Start
2. `.claude/agents/OPERATIONAL-RULES.md` - Add venv awareness section
3. `.claude/agents/onboarding.md` - Add setup step after project configuration

## Acceptance Criteria (Must Have)

- [ ] `./scripts/project setup` creates .venv and installs deps
- [ ] Python 3.9+ check runs before setup
- [ ] Clear error messages for all failure modes
- [ ] `--force` flag removes and recreates venv
- [ ] Corrupted venv detected (missing python binary)
- [ ] Pre-commit install runs if available (warning if not)
- [ ] Command appears in `./scripts/project --help`
- [ ] README Quick Start includes setup step

## Success Metrics

**Quantitative**:
- Setup completes in <60s on typical machine
- 0 errors when running on clean clone

**Qualitative**:
- Error messages guide users to resolution
- Idempotent (running twice works)

## Critical Implementation Details

### 1. Command Location in `scripts/project`

Add after the existing command handlers (around line 600). Follow the pattern of `cmd_reconfigure()`:

```python
def cmd_setup(args):
    """Set up virtual environment and install dependencies."""
    # Implementation from task spec
```

### 2. Error Handling Pattern

Use `capture_output=True` for subprocess calls to get error messages:

```python
result = subprocess.run(
    [str(pip), "install", "-e", ".[dev]"],
    capture_output=True, text=True
)
if result.returncode != 0:
    print(f"❌ Failed: {result.stderr[-500:]}")
    sys.exit(1)
```

### 3. Platform Considerations

The implementation uses `venv_dir / "bin" / "pip"` which works on macOS/Linux. Windows would need `Scripts/pip.exe` but the starter kit primarily targets macOS.

### 4. Pre-commit is Optional

Check if pre-commit exists before running:
```python
pre_commit = venv_dir / "bin" / "pre-commit"
if pre_commit.exists():
    # run pre-commit install
else:
    print("⚠️  pre-commit not found (non-critical)")
```

## Resources for Implementation

- **Existing command pattern**: `scripts/project` - see `cmd_reconfigure()` around line 485
- **Task specification**: `delegation/tasks/2-todo/ASK-0028-venv-setup-command.md`
- **Related ADR**: `docs/decisions/starter-kit-adr/KIT-ADR-0005-test-infrastructure-strategy.md`
- **Verify script reference**: `scripts/verify-setup.sh` (checks for venv)

## Time Estimate

2-3 hours total:
- Implementation: 1.5 hours
- Documentation updates: 30 min
- Manual testing: 30 min

## Starting Point

1. Run `./scripts/project start ASK-0028` to move task to in-progress
2. Open `scripts/project` and find the command dispatch section (~line 600)
3. Add `cmd_setup()` function following the implementation in the task spec
4. Add command routing in the dispatch section
5. Update help text
6. Test manually: `rm -rf .venv && ./scripts/project setup`
7. Update README and agent docs

## Questions for Planner

If blocked or need clarification:
- Update this handoff file with questions
- Or create a note in `.agent-context/`

## Evaluation History

- **Round 1**: NEEDS_REVISION - Missing error handling
- **Round 2**: NEEDS_REVISION - Requested automated tests (deemed impractical for venv scripts)
- **Coordinator decision**: Proceed with implementation; remaining concerns addressed or out-of-scope
- **Total cost**: ~$0.03

## Success Looks Like

After implementation:
```bash
# User clones starter kit
git clone https://github.com/user/new-project.git
cd new-project

# Setup works
./scripts/project setup
# ✅ Python 3.13.0
# 📦 Creating virtual environment...
# ✅ Created: /path/to/.venv
# 📦 Installing dependencies...
# ✅ Dependencies installed
# 🔧 Installing pre-commit hooks...
# ✅ Pre-commit hooks installed
# ============================================================
# ✅ Setup complete!
# To activate: source .venv/bin/activate

# Dependencies available
source .venv/bin/activate
python -c "import gql; print('gql available')"
# gql available
```

## Notes

- This task fixes the ROOT CAUSE of the gql issue
- A separate fix already handles the SYMPTOM (graceful test skipping)
- Focus on macOS; Linux works by default, Windows is out of scope

---

**Task File**: `delegation/tasks/2-todo/ASK-0028-venv-setup-command.md`
**Evaluation Logs**: `.adversarial/logs/ASK-0028-venv-setup-command-PLAN-EVALUATION.md`
**Handoff Date**: 2025-02-01
**Coordinator**: Planner
