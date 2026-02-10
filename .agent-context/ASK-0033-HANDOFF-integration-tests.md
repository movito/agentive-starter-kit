# ASK-0033: Agent Creation Integration Tests - Implementation Handoff

**Date**: 2026-02-10
**From**: Coordinator (main session)
**To**: feature-developer
**Task**: `delegation/tasks/3-in-progress/ASK-0033-agent-creation-automation.md`
**Plan**: `.adversarial/artifacts/ASK-0033-v2-reimplementation-plan.md`
**Status**: Ready for implementation
**Evaluation**: Plan evaluated by GPT-5.2 (2 rounds, $0.09 total). Round 2 NEEDS_REVISION on 4 items being addressed during implementation.

---

## Task Summary

Write the integration and concurrency test file for `scripts/create-agent.sh` as part of the ASK-0033 v2 clean reimplementation. This is the **TDD Red Phase** — tests define expected behavior before the script exists.

## Current Situation

PR #12 (original ASK-0033 implementation) was closed after 25 review rounds with 18 bugs. We're reimplementing cleanly from `main`. The branch `feature/ASK-0033-v2-agent-creation` is already created and the `setup_temp_project()` fixture is already committed to `tests/conftest.py`.

**Coordination note**: Another feature-developer is writing `tests/test_create_agent.py` (unit tests) in parallel. You are writing the integration tests. These files are independent — no coordination needed beyond using the same `run_script()` pattern.

## Your Mission

Create two files:
1. `tests/integration/__init__.py` (empty)
2. `tests/integration/test_concurrent_agent_creation.py` with 4 test classes (~9 tests)

These tests exercise concurrent access, sequential multi-agent creation, lock recovery, and end-to-end workflows.

## Branch & Git

- **Branch**: `feature/ASK-0033-v2-agent-creation` (ALREADY EXISTS - do NOT create a new branch)
- **Task status**: Already in `3-in-progress/` (do NOT run `./scripts/project start`)
- **Commit when done**: Yes, commit your test files with message format `test(ASK-0033): Add integration tests for concurrent agent creation`
- **Pull before commit**: Run `git pull origin feature/ASK-0033-v2-agent-creation` first in case the unit test agent committed

## Acceptance Criteria (Must Have)

- [ ] **Files created**: `tests/integration/__init__.py` and `tests/integration/test_concurrent_agent_creation.py`
- [ ] **4 test classes, ~9 tests**: Covering concurrency, locking, sequential creation, end-to-end
- [ ] **Bug ledger coverage**: T2 (lock cleanup), T5 (stale lock creation), S5 (stale detection), S6 (atomic locking)
- [ ] **Test design rules**: No conditional assertions, no unused variables, returncode checked first
- [ ] **Lock cleanup**: Once per `setup_method`, not per `run_script` call (fixes T2)
- [ ] **Slow marker**: All tests marked with `@pytest.mark.slow`
- [ ] **Black/isort clean**: File passes `black --check` and `isort --check`

## Test Classes Required

| Class | Tests | What it validates |
|-------|-------|-------------------|
| `TestSequentialCreation` | 2 | Create multiple agents in sequence, all present in launcher |
| `TestConcurrentExecution` | 3 | ThreadPoolExecutor with 5 workers, exactly 1 succeeds, others get lock error (exit 2) |
| `TestLockRecovery` | 2 | Stale lock dir with dead PID recovered; fresh lock with live PID blocks |
| `TestEndToEnd` | 2 | Create agent + verify launcher works; `--force` update + `--dry-run` |

## Critical Implementation Details

### 1. run_script() Helper (same as unit tests)

```python
def run_script(
    args: list[str],
    project_dir: Path,
    cleanup_lock: bool = True,
    env: dict | None = None,
) -> subprocess.CompletedProcess:
    """Run create-agent.sh with given args in a temp project dir."""
    script = Path(__file__).resolve().parent.parent.parent / "scripts" / "create-agent.sh"
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

Note: `Path(__file__).resolve().parent.parent.parent` because this file is in `tests/integration/`.

### 2. Concurrent Test Pattern (fixes T2)

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

class TestConcurrentExecution:
    def setup_method(self):
        self.project_dir = setup_temp_project()
        # Clean lock ONCE at setup, not per-call (fixes T2)
        lock_dir = Path("/tmp/agent-creation.lock")
        if lock_dir.exists():
            shutil.rmtree(lock_dir)

    def test_concurrent_creation_only_one_succeeds(self):
        """5 concurrent agents: exactly 1 should succeed, rest get lock error."""
        agents = [f"concurrent-agent-{i}" for i in range(5)]

        def create_agent(name):
            return run_script(
                [name, f"Test agent {name}"],
                self.project_dir,
                cleanup_lock=False,  # Don't clean per-call!
            )

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(create_agent, name): name for name in agents}
            results = {name: future.result() for future, name in futures.items()}

        successes = [n for n, r in results.items() if r.returncode == 0]
        lock_errors = [n for n, r in results.items() if r.returncode == 2]

        assert len(successes) == 1, f"Expected 1 success, got {len(successes)}: {successes}"
        assert len(lock_errors) == 4, f"Expected 4 lock errors, got {len(lock_errors)}"
```

### 3. Stale Lock Test (fixes T5)

```python
class TestLockRecovery:
    def test_stale_lock_with_dead_pid_is_recovered(self):
        """Script should detect and remove lock from dead process."""
        lock_dir = Path("/tmp/agent-creation.lock")
        lock_dir.mkdir(exist_ok=True)

        # Find a dead PID (not currently running)
        dead_pid = 99999
        while True:
            try:
                os.kill(dead_pid, 0)
                dead_pid -= 1  # PID exists, try another
            except ProcessLookupError:
                break  # Found a dead PID
            except PermissionError:
                dead_pid -= 1  # PID exists but we can't signal it
                continue

        # Write stale lock metadata
        owner_file = lock_dir / "owner"
        owner_file.write_text(
            f"pid={dead_pid}\ntoken=deadbeef\ntime={int(time.time()) - 120}\n"
        )

        result = run_script(
            ["recovery-agent", "Test recovery"],
            self.project_dir,
            cleanup_lock=False,  # Don't clean - we want to test recovery
        )
        assert result.returncode == 0, f"Should recover stale lock: {result.stderr}"
```

### 4. Locking Design (from revised plan)

The script uses `mkdir`-based atomic locking:
- Lock directory: `/tmp/agent-creation.lock/`
- Owner metadata: `/tmp/agent-creation.lock/owner` with pid, token, timestamp
- Stale detection: PID dead OR (PID alive AND age > threshold)
- Threshold configurable via `CREATE_AGENT_LOCK_STALE_SECS` env var (default 60s)

### 5. Slow Test Marker

All integration tests must be marked:

```python
import pytest

pytestmark = pytest.mark.slow
```

This ensures they're skipped during pre-commit (which only runs fast tests) but included in `./scripts/ci-check.sh`.

## Resources

- **Plan**: `.adversarial/artifacts/ASK-0033-v2-reimplementation-plan.md` (locking design, bug ledger)
- **Existing test patterns**: `tests/test_project_script.py`
- **Fixture**: `tests/conftest.py` → `setup_temp_project()`
- **pytest config**: `pyproject.toml` (check marker registration)

## Success Looks Like

- `tests/integration/__init__.py` exists (empty)
- `tests/integration/test_concurrent_agent_creation.py` exists with 9 well-structured tests
- `python3 -m py_compile tests/integration/test_concurrent_agent_creation.py` succeeds
- `black --check tests/integration/test_concurrent_agent_creation.py` passes
- Tests are committed on `feature/ASK-0033-v2-agent-creation`
- T2 (lock cleanup) and T5 (stale lock) are specifically addressed

---

**Task File**: `delegation/tasks/3-in-progress/ASK-0033-agent-creation-automation.md`
**Handoff Date**: 2026-02-10
**Coordinator**: Main session
