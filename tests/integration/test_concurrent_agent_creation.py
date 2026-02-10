"""
Integration tests for concurrent agent creation via scripts/create-agent.sh.

Covers: concurrency (S6), locking (S5, T2, T5), sequential creation,
and end-to-end workflows. All tests are marked @pytest.mark.slow and
require the create-agent.sh script to exist.

Bug ledger coverage:
  T2 - Lock cleanup once per setup_method, not per run_script call
  T5 - Stale lock test creates lock dir with dead PID metadata
  S5 - Stale lock detection via PID validity + age check
  S6 - Atomic locking via mkdir primitive
"""

import os
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pytest

from conftest import CREATE_AGENT_LOCK_DIR as LOCK_DIR
from conftest import run_create_agent_script as run_script
from conftest import setup_temp_project

pytestmark = pytest.mark.slow


class TestSequentialCreation:
    """Create multiple agents one after another, verify all present in launcher."""

    def setup_method(self):
        self.project_dir = setup_temp_project()
        if LOCK_DIR.exists():
            shutil.rmtree(LOCK_DIR)

    def teardown_method(self):
        if LOCK_DIR.exists():
            shutil.rmtree(LOCK_DIR)
        shutil.rmtree(self.project_dir, ignore_errors=True)

    def test_two_agents_created_sequentially(self):
        """Two agents created in sequence both succeed."""
        result_a = run_script(["alpha-agent", "First agent"], self.project_dir)
        assert result_a.returncode == 0, f"First agent failed: {result_a.stderr}"

        result_b = run_script(["beta-agent", "Second agent"], self.project_dir)
        assert result_b.returncode == 0, f"Second agent failed: {result_b.stderr}"

        # Both agent files should exist
        alpha_file = self.project_dir / ".claude" / "agents" / "alpha-agent.md"
        beta_file = self.project_dir / ".claude" / "agents" / "beta-agent.md"
        assert alpha_file.exists(), "alpha-agent.md not created"
        assert beta_file.exists(), "beta-agent.md not created"

    def test_sequential_agents_all_in_launcher(self):
        """Three agents created sequentially all appear in launcher."""
        names = ["seq-agent-1", "seq-agent-2", "seq-agent-3"]
        for name in names:
            result = run_script([name, f"Description for {name}"], self.project_dir)
            assert result.returncode == 0, f"{name} failed: {result.stderr}"

        launcher_text = (self.project_dir / "agents" / "launch").read_text()
        for name in names:
            assert name in launcher_text, f"{name} missing from launcher"


class TestConcurrentExecution:
    """Concurrent agent creation: exactly one succeeds, others get lock error.

    Bug ledger: S6 (atomic locking via mkdir), T2 (lock cleanup per setup).
    """

    def setup_method(self):
        self.project_dir = setup_temp_project()
        # Clean lock ONCE at setup, not per-call (fixes T2)
        if LOCK_DIR.exists():
            shutil.rmtree(LOCK_DIR)

    def teardown_method(self):
        if LOCK_DIR.exists():
            shutil.rmtree(LOCK_DIR)
        shutil.rmtree(self.project_dir, ignore_errors=True)

    def test_concurrent_creation_only_one_succeeds(self):
        """5 concurrent agents: exactly 1 succeeds, rest get lock error (exit 2)."""
        agents = [f"concurrent-agent-{i}" for i in range(5)]
        # WORK_DELAY=3 ensures lock holder keeps lock while others try
        # LOCK_WAIT_SECS=0 ensures losers fail immediately instead of retrying
        concurrent_env = {
            "CREATE_AGENT_LOCK_WAIT_SECS": "0",
            "CREATE_AGENT_WORK_DELAY": "3",
        }

        def create_agent(name):
            return run_script(
                [name, f"Test agent {name}"],
                self.project_dir,
                cleanup_lock=False,  # Don't clean per-call (T2)
                env=concurrent_env,
            )

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(create_agent, name): name for name in agents}
            results = {name: future.result() for future, name in futures.items()}

        successes = [n for n, r in results.items() if r.returncode == 0]
        lock_errors = [n for n, r in results.items() if r.returncode == 2]

        assert (
            len(successes) == 1
        ), f"Expected 1 success, got {len(successes)}: {successes}"
        assert (
            len(lock_errors) == 4
        ), f"Expected 4 lock errors, got {len(lock_errors)}: {lock_errors}"

    def test_concurrent_winner_file_exists(self):
        """The one agent that wins the lock should have its file created."""
        agents = [f"race-agent-{i}" for i in range(3)]
        concurrent_env = {
            "CREATE_AGENT_LOCK_WAIT_SECS": "0",
            "CREATE_AGENT_WORK_DELAY": "3",
        }

        def create_agent(name):
            return run_script(
                [name, f"Test agent {name}"],
                self.project_dir,
                cleanup_lock=False,
                env=concurrent_env,
            )

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(create_agent, name): name for name in agents}
            results = {name: future.result() for future, name in futures.items()}

        winners = [n for n, r in results.items() if r.returncode == 0]
        assert len(winners) == 1, f"Expected 1 winner, got {len(winners)}"

        winner = winners[0]
        agent_file = self.project_dir / ".claude" / "agents" / f"{winner}.md"
        assert agent_file.exists(), f"Winner's agent file not created: {winner}"

    def test_concurrent_launcher_not_corrupted(self):
        """After concurrent attempts, launcher file is still valid bash."""
        agents = [f"corrupt-check-{i}" for i in range(5)]
        concurrent_env = {
            "CREATE_AGENT_LOCK_WAIT_SECS": "0",
            "CREATE_AGENT_WORK_DELAY": "3",
        }

        def create_agent(name):
            return run_script(
                [name, f"Test agent {name}"],
                self.project_dir,
                cleanup_lock=False,
                env=concurrent_env,
            )

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(create_agent, name): name for name in agents}
            for future in as_completed(futures):
                future.result()  # Wait for all to finish

        # Launcher should still be valid bash syntax
        launcher_path = self.project_dir / "agents" / "launch"
        syntax_check = subprocess.run(
            ["bash", "-n", str(launcher_path)],
            capture_output=True,
            text=True,
        )
        assert (
            syntax_check.returncode == 0
        ), f"Launcher has invalid bash syntax: {syntax_check.stderr}"


class TestLockRecovery:
    """Lock recovery: stale locks cleaned up, active locks respected.

    Bug ledger: T5 (stale lock with dead PID), S5 (stale detection).
    """

    def setup_method(self):
        self.project_dir = setup_temp_project()
        if LOCK_DIR.exists():
            shutil.rmtree(LOCK_DIR)

    def teardown_method(self):
        if LOCK_DIR.exists():
            shutil.rmtree(LOCK_DIR)
        shutil.rmtree(self.project_dir, ignore_errors=True)

    def test_stale_lock_with_dead_pid_is_recovered(self):
        """Script detects and removes lock from a dead process (fixes T5, S5)."""
        LOCK_DIR.mkdir(exist_ok=True)

        # Find a PID that is definitely not running
        dead_pid = 99999
        while True:
            try:
                os.kill(dead_pid, 0)
                dead_pid -= 1
            except ProcessLookupError:
                break
            except PermissionError:
                dead_pid -= 1
                continue

        # Write stale lock metadata with dead PID
        owner_file = LOCK_DIR / "owner"
        owner_file.write_text(
            f"pid={dead_pid}\ntoken=deadbeef\ntime={int(time.time()) - 120}\n"
        )

        result = run_script(
            ["recovery-agent", "Test recovery"],
            self.project_dir,
            cleanup_lock=False,  # Don't clean — we test recovery
        )
        assert result.returncode == 0, f"Should recover stale lock: {result.stderr}"

    def test_active_lock_with_live_pid_blocks(self):
        """Script should not steal a lock held by a live process."""
        LOCK_DIR.mkdir(exist_ok=True)

        # Use our own PID — definitely alive
        live_pid = os.getpid()
        owner_file = LOCK_DIR / "owner"
        owner_file.write_text(
            f"pid={live_pid}\ntoken=livetoken\ntime={int(time.time())}\n"
        )

        result = run_script(
            ["blocked-agent", "Should be blocked"],
            self.project_dir,
            cleanup_lock=False,
            env={"CREATE_AGENT_LOCK_WAIT_SECS": "2"},
        )
        assert (
            result.returncode == 2
        ), f"Expected lock error (exit 2), got {result.returncode}: {result.stderr}"


class TestEndToEnd:
    """End-to-end: create agent, verify launcher, test --force and --dry-run."""

    def setup_method(self):
        self.project_dir = setup_temp_project()
        if LOCK_DIR.exists():
            shutil.rmtree(LOCK_DIR)

    def teardown_method(self):
        if LOCK_DIR.exists():
            shutil.rmtree(LOCK_DIR)
        shutil.rmtree(self.project_dir, ignore_errors=True)

    def test_create_and_launcher_integration(self):
        """Create an agent, then verify the launcher can list it."""
        result = run_script(
            ["e2e-agent", "End-to-end test agent"],
            self.project_dir,
        )
        assert result.returncode == 0, f"Creation failed: {result.stderr}"

        # Agent file should exist
        agent_file = self.project_dir / ".claude" / "agents" / "e2e-agent.md"
        assert agent_file.exists(), "Agent file not created"

        # Launcher should reference the agent
        launcher_text = (self.project_dir / "agents" / "launch").read_text()
        assert "e2e-agent" in launcher_text, "Agent not in launcher"

    def test_force_update_and_dry_run(self):
        """--force overwrites existing agent; --dry-run shows changes only."""
        # Create agent first
        result = run_script(
            ["update-agent", "Original description"],
            self.project_dir,
        )
        assert result.returncode == 0, f"Initial creation failed: {result.stderr}"

        # --force should overwrite without error
        result_force = run_script(
            ["update-agent", "Updated description", "--force"],
            self.project_dir,
        )
        assert (
            result_force.returncode == 0
        ), f"--force update failed: {result_force.stderr}"

        # --dry-run should succeed without modifying files
        result_dry = run_script(
            ["dryrun-agent", "Dry run test", "--dry-run"],
            self.project_dir,
        )
        assert result_dry.returncode == 0, f"--dry-run failed: {result_dry.stderr}"

        # Dry-run agent file should NOT exist
        dry_file = self.project_dir / ".claude" / "agents" / "dryrun-agent.md"
        assert not dry_file.exists(), "Dry-run should not create agent file"
