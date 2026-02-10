# ASK-0033: Agent Creation Unit Tests - Implementation Handoff

**Date**: 2026-02-10
**From**: Coordinator (main session)
**To**: feature-developer
**Task**: `delegation/tasks/3-in-progress/ASK-0033-agent-creation-automation.md`
**Plan**: `.adversarial/artifacts/ASK-0033-v2-reimplementation-plan.md`
**Status**: Ready for implementation
**Evaluation**: Plan evaluated by GPT-5.2 (2 rounds, $0.09 total). Round 2 NEEDS_REVISION on 4 items being addressed during implementation.

---

## Task Summary

Write the unit test file for `scripts/create-agent.sh` as part of the ASK-0033 v2 clean reimplementation. This is the **TDD Red Phase** — tests should be written to define expected behavior before the script exists.

## Current Situation

PR #12 (original ASK-0033 implementation) was closed after 25 review rounds with 18 bugs. We're reimplementing cleanly from `main`. The branch `feature/ASK-0033-v2-agent-creation` is already created and the `setup_temp_project()` fixture is already committed to `tests/conftest.py`.

## Your Mission

Create `tests/test_create_agent.py` with 9 test classes (~30 tests) that define the complete behavioral contract for `scripts/create-agent.sh`.

**Important**: The script does NOT exist yet. Tests will fail (TDD Red Phase). That's expected. Write tests that define what the script SHOULD do. Use `pytest.mark.xfail` or skip decorators if needed for tests that can't run without the script, but prefer tests that simply assert against `subprocess.run` results.

## Branch & Git

- **Branch**: `feature/ASK-0033-v2-agent-creation` (ALREADY EXISTS - do NOT create a new branch)
- **Task status**: Already in `3-in-progress/` (do NOT run `./scripts/project start`)
- **Commit when done**: Yes, commit your test file with message format `test(ASK-0033): Add unit tests for create-agent.sh`

## Acceptance Criteria (Must Have)

- [ ] **File created**: `tests/test_create_agent.py` with 9 test classes
- [ ] **30+ tests**: Covering all acceptance criteria from the plan
- [ ] **Bug ledger coverage**: Every testable bug (S1-S10, T1-T7) has a mapped regression test
- [ ] **Test design rules**: No conditional assertions, no unused variables, returncode checked first
- [ ] **Golden-file tests**: At least 1 test comparing launcher output against expected fixture
- [ ] **Black/isort clean**: File passes `black --check` and `isort --check`
- [ ] **Imports valid**: All imports resolve (no missing dependencies)

## Test Classes Required

| Class | Tests | What it validates |
|-------|-------|-------------------|
| `TestScriptExists` | 2 | Script exists, has `#!/bin/bash` shebang, is executable |
| `TestHelpUsage` | 3 | `--help` shows usage, exits 0, documents all options |
| `TestInputValidation` | 5 | Name format, description required, invalid chars rejected, model validation |
| `TestDuplicateDetection` | 3 | Duplicate rejected (exit 1), `--force` overwrites, `--dry-run` reports |
| `TestTemplateProcessing` | 4 | All placeholders replaced, special chars in description (S1), no unresolved brackets (T7) |
| `TestLauncherIntegration` | 5 | All 3 arrays updated, indentation correct (golden-file), no duplicates with `--force` (S4) |
| `TestExitCodes` | 3 | Exit 0 success, exit 1 user error, exit 2 system error |
| `TestLogging` | 3 | Log file created, JSON valid (S10), required fields present |
| `TestDryRun` | 2 | No files modified, reports planned actions |

## Critical Implementation Details

### 1. run_script() Helper

Every test should use a shared helper:

```python
def run_script(
    args: list[str],
    project_dir: Path,
    cleanup_lock: bool = True,
    env: dict | None = None,
) -> subprocess.CompletedProcess:
    """Run create-agent.sh with given args in a temp project dir."""
    script = Path(__file__).resolve().parent.parent / "scripts" / "create-agent.sh"
    if cleanup_lock:
        lock_dir = Path("/tmp/agent-creation.lock")
        if lock_dir.exists():
            shutil.rmtree(lock_dir)

    run_env = os.environ.copy()
    run_env["CREATE_AGENT_PROJECT_ROOT"] = str(project_dir)
    if env:
        run_env.update(env)

    return subprocess.run(
        ["bash", str(script)] + args,
        capture_output=True,
        text=True,
        timeout=30,
        env=run_env,
    )
```

### 2. Fixture Usage

```python
from tests.conftest import setup_temp_project

class TestSomething:
    def setup_method(self):
        self.project_dir = setup_temp_project()

    def teardown_method(self):
        shutil.rmtree(self.project_dir, ignore_errors=True)
```

### 3. Assertion Pattern (prevents T4, T6)

```python
# CORRECT: Assert returncode first, then output
result = run_script(["--help"], self.project_dir)
assert result.returncode == 0, f"Expected exit 0, got {result.returncode}: {result.stderr}"
assert "Usage:" in result.stdout

# WRONG: Don't wrap in conditionals
# if result.returncode == 0:
#     assert "Usage:" in result.stdout  # NEVER DO THIS
```

### 4. Placeholder Detection (prevents T7)

```python
import re
# CORRECT: Use regex
unresolved = re.findall(r"\[[A-Z][A-Za-z -]+\]", content)
assert len(unresolved) == 0, f"Unresolved placeholders: {unresolved}"

# WRONG: Don't use string containment
# assert "[" not in content or "]" not in content
```

### 5. Golden-File Test for Launcher

Create a known-input launcher fixture, run the script, compare specific sections of the output against expected values. Focus on the three sections: `agent_order`, `serena_agents`, `get_agent_icon`.

### 6. CLI Contract (from plan's Definition of Done)

```
Usage: scripts/create-agent.sh <name> <description> [options]

Required:
  <name>            Agent name (lowercase, hyphens allowed, 2-30 chars)
  <description>     One-sentence description (quoted string)

Options:
  --model <id>      Claude model ID (default: claude-sonnet-4-5-20250929)
  --emoji <char>    Icon emoji for launcher menu (default: auto-assigned)
  --serena          Enable Serena auto-activation for this agent
  --force           Overwrite existing agent (replaces file + launcher entries)
  --dry-run         Show what would be done without making changes
  --help            Show usage information

Exit Codes:
  0  Success
  1  User error (invalid input, duplicate name, missing template)
  2  System error (lock timeout, file I/O failure, missing dependencies)
```

## Resources

- **Plan**: `.adversarial/artifacts/ASK-0033-v2-reimplementation-plan.md` (full bug ledger, design decisions)
- **Existing test patterns**: `tests/test_project_script.py`, `tests/test_uv_detection.py`
- **Fixture**: `tests/conftest.py` → `setup_temp_project()`
- **Template**: `.claude/agents/AGENT-TEMPLATE.md`
- **Launcher structure**: `agents/launch` (lines 44-55: agent_order, 162-170: serena_agents, 237-248: get_agent_icon)

## Success Looks Like

- `tests/test_create_agent.py` exists with 30+ well-structured tests
- `python3 -m py_compile tests/test_create_agent.py` succeeds (no syntax errors)
- `black --check tests/test_create_agent.py` passes
- Tests are committed on `feature/ASK-0033-v2-agent-creation`
- Every bug from the ledger (S1-S10, T1-T7) has a corresponding regression test

---

**Task File**: `delegation/tasks/3-in-progress/ASK-0033-agent-creation-automation.md`
**Handoff Date**: 2026-02-10
**Coordinator**: Main session
