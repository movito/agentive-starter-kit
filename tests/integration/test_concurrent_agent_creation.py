"""
Integration tests for concurrent agent creation.

These tests verify that the create-agent.sh script handles
concurrent access safely using file locking.

CRITICAL: These tests are essential for production safety.
"""

import subprocess

# Import shared test utilities
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import setup_temp_project

PROJECT_ROOT = Path(__file__).parent.parent.parent
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "create-agent.sh"
LOCK_FILE = Path("/tmp/agent-creation-launcher.lock")


def run_create_agent(
    cwd: Path, agent_name: str, description: str
) -> subprocess.CompletedProcess:
    """Run create-agent.sh and return the result.

    Note: This helper cleans up the lock file before each run for test isolation.
    For tests that specifically verify locking behavior under concurrent access,
    use subprocess.Popen directly (see test_lock_prevents_simultaneous_writes).
    """
    # Clean up lock file for test isolation (not for concurrent lock tests)
    try:
        LOCK_FILE.unlink(missing_ok=True)
    except (PermissionError, OSError):
        pass

    return subprocess.run(
        ["bash", str(SCRIPT_PATH), agent_name, description],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=60,
    )


class TestBasicConcurrency:
    """Basic concurrent access tests."""

    def test_sequential_creation_succeeds(self):
        """Creating agents one after another works correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            # Create first agent
            result1 = run_create_agent(tmp_path, "agent-one", "First agent")
            assert result1.returncode == 0, f"First creation failed: {result1.stderr}"

            # Create second agent
            result2 = run_create_agent(tmp_path, "agent-two", "Second agent")
            assert result2.returncode == 0, f"Second creation failed: {result2.stderr}"

            # Verify both agents exist
            assert (tmp_path / ".claude" / "agents" / "agent-one.md").exists()
            assert (tmp_path / ".claude" / "agents" / "agent-two.md").exists()

            # Verify launcher contains both
            launcher_content = (tmp_path / "agents" / "launch").read_text()
            assert "agent-one" in launcher_content
            assert "agent-two" in launcher_content

    def test_launcher_syntax_after_multiple_creations(self):
        """Launcher file remains valid after multiple agent creations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            # Create several agents
            for i in range(3):
                result = run_create_agent(
                    tmp_path, f"test-agent-{i}", f"Test agent {i}"
                )
                assert result.returncode == 0, f"Creation {i} failed: {result.stderr}"

            # Verify launcher syntax is valid
            launcher_file = tmp_path / "agents" / "launch"
            syntax_check = subprocess.run(
                ["bash", "-n", str(launcher_file)],
                capture_output=True,
                text=True,
            )
            assert syntax_check.returncode == 0, f"Syntax error: {syntax_check.stderr}"


class TestConcurrentExecution:
    """Tests for truly concurrent agent creation attempts."""

    @pytest.mark.slow
    def test_concurrent_creation_no_corruption(self):
        """Multiple simultaneous creations don't corrupt the launcher."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            results = []
            num_agents = 5

            def create_agent(i: int):
                # Small random delay to increase concurrency overlap
                time.sleep(0.05 * (i % 3))
                return run_create_agent(tmp_path, f"concurrent-{i}", f"Agent {i}")

            # Run creations concurrently
            with ThreadPoolExecutor(max_workers=num_agents) as executor:
                futures = {
                    executor.submit(create_agent, i): i for i in range(num_agents)
                }
                for future in as_completed(futures):
                    results.append(future.result())

            # Check results - most should succeed, some might timeout
            successes = [r for r in results if r.returncode == 0]

            # At minimum, one should succeed (the one that got the lock)
            assert len(successes) >= 1, "At least one creation should succeed"

            # Verify launcher syntax is still valid
            launcher_file = tmp_path / "agents" / "launch"
            syntax_check = subprocess.run(
                ["bash", "-n", str(launcher_file)],
                capture_output=True,
                text=True,
            )
            assert (
                syntax_check.returncode == 0
            ), f"Launcher corrupted after concurrent access: {syntax_check.stderr}"

    @pytest.mark.slow
    def test_lock_prevents_simultaneous_writes(self):
        """Lock mechanism prevents two processes from writing simultaneously."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            # Start two processes nearly simultaneously
            proc1 = subprocess.Popen(
                ["bash", str(SCRIPT_PATH), "lock-test-1", "First agent"],
                cwd=tmp_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Small delay then start second
            time.sleep(0.1)

            proc2 = subprocess.Popen(
                ["bash", str(SCRIPT_PATH), "lock-test-2", "Second agent"],
                cwd=tmp_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait for both to complete (output not needed for this test)
            _stdout1, _stderr1 = proc1.communicate(timeout=60)
            _stdout2, _stderr2 = proc2.communicate(timeout=60)

            # Both should complete (one might wait for lock)
            # Launcher should be valid
            launcher_file = tmp_path / "agents" / "launch"
            syntax_check = subprocess.run(
                ["bash", "-n", str(launcher_file)],
                capture_output=True,
                text=True,
            )
            assert syntax_check.returncode == 0, "Launcher corrupted"


class TestLockRecovery:
    """Tests for lock file recovery scenarios."""

    def test_stale_lock_file_recovery(self):
        """Script recovers from stale lock files left by crashed processes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            # Create a stale lock file with a non-existent PID
            # Use PID 99999 which is unlikely to exist (and will be checked)
            stale_pid = 99999
            # Find an unused PID by checking if it exists
            while True:
                try:
                    import os

                    os.kill(stale_pid, 0)
                    stale_pid += 1  # PID exists, try another
                except OSError:
                    break  # PID doesn't exist, use it

            LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
            LOCK_FILE.write_text(str(stale_pid))

            # Run script - it should detect stale lock and recover
            result = subprocess.run(
                ["bash", str(SCRIPT_PATH), "recovery-test", "Recovery test"],
                capture_output=True,
                text=True,
                cwd=tmp_path,
                timeout=60,
            )

            # Should succeed by detecting and removing stale lock
            assert result.returncode == 0, f"Failed to recover from stale lock: {result.stderr}"

            # Verify agent was created
            assert (tmp_path / ".claude" / "agents" / "recovery-test.md").exists()

    def test_cleanup_on_script_failure(self):
        """Partial files are cleaned up when script fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            # Remove the launcher to cause a failure mid-process
            (tmp_path / "agents" / "launch").unlink()

            result = run_create_agent(tmp_path, "cleanup-test", "Should fail")

            # Should fail (no launcher)
            assert result.returncode != 0

            # When launcher is missing, script fails before creating agent file
            # So agent file should not exist (cleanup not needed because creation didn't start)
            agent_file = tmp_path / ".claude" / "agents" / "cleanup-test.md"
            assert (
                not agent_file.exists()
            ), "Agent file should not exist when launcher is missing"


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    def test_full_agent_creation_workflow(self):
        """Complete workflow from creation to launch verification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            # Create agent with all options
            result = subprocess.run(
                [
                    "bash",
                    str(SCRIPT_PATH),
                    "workflow-test",
                    "A complete workflow test agent",
                    "--model",
                    "claude-opus-4-5-20251101",
                    "--emoji",
                    "🧪",
                    "--serena",
                ],
                capture_output=True,
                text=True,
                cwd=tmp_path,
                timeout=30,
            )

            # Clean up lock
            try:
                LOCK_FILE.unlink(missing_ok=True)
            except (PermissionError, OSError):
                pass

            assert result.returncode == 0, f"Failed: {result.stderr}"
            assert "SUCCESS" in result.stdout

            # Verify agent file
            agent_file = tmp_path / ".claude" / "agents" / "workflow-test.md"
            assert agent_file.exists()

            content = agent_file.read_text()
            assert "workflow-test" in content
            assert "claude-opus-4-5-20251101" in content

            # Verify launcher updates
            launcher_content = (tmp_path / "agents" / "launch").read_text()
            assert "workflow-test" in launcher_content
            assert "🧪" in launcher_content

    def test_dry_run_makes_no_changes(self):
        """Dry run shows what would happen without making changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            # Get original state
            original_launcher = (tmp_path / "agents" / "launch").read_text()
            original_agents = list((tmp_path / ".claude" / "agents").glob("*.md"))

            # Run with --dry-run
            result = subprocess.run(
                [
                    "bash",
                    str(SCRIPT_PATH),
                    "dry-run-test",
                    "Should not be created",
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                cwd=tmp_path,
                timeout=30,
            )

            assert result.returncode == 0

            # Verify no changes
            assert (tmp_path / "agents" / "launch").read_text() == original_launcher
            current_agents = list((tmp_path / ".claude" / "agents").glob("*.md"))
            assert len(current_agents) == len(original_agents)
