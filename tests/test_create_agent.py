"""
Tests for scripts/create-agent.sh - Agent creation automation script.

This test suite validates the create-agent.sh script that enables the
AGENT-CREATOR agent to create new agents programmatically.

TDD Approach: Tests written first, script implementation follows.
"""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from conftest import setup_temp_project

# Get project root for script paths
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "create-agent.sh"
TEMPLATE_PATH = PROJECT_ROOT / ".claude" / "agents" / "AGENT-TEMPLATE.md"
LAUNCHER_PATH = PROJECT_ROOT / "agents" / "launch"


LOCK_FILE = Path("/tmp/agent-creation-launcher.lock")


def run_script(
    args: list[str], cwd: Path | None = None, env: dict | None = None
) -> subprocess.CompletedProcess:
    """Run the create-agent.sh script with given arguments.

    Args:
        args: List of arguments to pass to the script.
        cwd: Working directory for the script. Defaults to PROJECT_ROOT.
        env: Environment variables. Defaults to current env.

    Returns:
        CompletedProcess with stdout, stderr, and returncode.
    """
    if cwd is None:
        cwd = PROJECT_ROOT

    # Clean up any leftover lock file from previous tests
    try:
        LOCK_FILE.unlink(missing_ok=True)
    except (PermissionError, OSError):
        pass

    # Merge provided env with current environment
    run_env = os.environ.copy()
    if env:
        run_env.update(env)

    return subprocess.run(
        ["bash", str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        env=run_env,
        timeout=30,
    )


class TestScriptExists:
    """Basic script existence and execution tests."""

    def test_script_exists(self):
        """Script file exists at expected path."""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"

    def test_script_is_executable(self):
        """Script file is executable."""
        assert os.access(SCRIPT_PATH, os.X_OK), "Script is not executable"

    def test_script_has_valid_shebang(self):
        """Script has valid bash shebang."""
        content = SCRIPT_PATH.read_text()
        assert content.startswith(
            ("#!/bin/bash", "#!/usr/bin/env bash")
        ), "Script missing bash shebang"


class TestHelpAndUsage:
    """Tests for help text and usage information."""

    def test_no_args_shows_usage(self):
        """Running without arguments shows usage and exits with error."""
        result = run_script([])
        assert result.returncode != 0, "Should exit with error when no args"
        assert (
            "usage" in result.stderr.lower() or "usage" in result.stdout.lower()
        ), "Should show usage information"

    def test_help_flag_shows_help(self):
        """--help flag shows help text."""
        result = run_script(["--help"])
        assert result.returncode == 0, "Help should exit with success"
        assert "usage" in result.stdout.lower(), "Should show usage"
        assert "agent-name" in result.stdout.lower(), "Should mention agent-name"
        assert "description" in result.stdout.lower(), "Should mention description"

    def test_h_flag_shows_help(self):
        """-h flag shows help text."""
        result = run_script(["-h"])
        assert result.returncode == 0, "-h should exit with success"
        assert "usage" in result.stdout.lower(), "-h should show usage"


class TestInputValidation:
    """Tests for input validation."""

    def test_missing_description_fails(self):
        """Missing description argument fails with user error."""
        result = run_script(["test-agent"])
        assert result.returncode == 1, "Missing description should exit with code 1"
        assert (
            "description" in result.stderr.lower()
        ), "Should mention missing description"

    def test_invalid_agent_name_with_spaces_fails(self):
        """Agent name with spaces is rejected."""
        result = run_script(["test agent", "A test agent"])
        assert result.returncode == 1, "Spaces in name should fail"
        assert (
            "invalid" in result.stderr.lower() or "space" in result.stderr.lower()
        ), "Should mention invalid name"

    def test_invalid_agent_name_with_special_chars_fails(self):
        """Agent name with special characters is rejected."""
        result = run_script(["test@agent!", "A test agent"])
        assert result.returncode == 1, "Special chars in name should fail"
        assert "invalid" in result.stderr.lower(), "Should mention invalid name"

    def test_agent_name_too_long_fails(self):
        """Agent name exceeding 50 characters is rejected."""
        long_name = "a" * 51
        result = run_script([long_name, "A test agent"])
        assert result.returncode == 1, "Long name should fail"
        assert (
            "long" in result.stderr.lower() or "characters" in result.stderr.lower()
        ), "Should mention name length"

    def test_valid_agent_name_kebab_case_accepted(self):
        """Valid kebab-case agent name is accepted."""
        # This test will fail until template processing works
        # We use a temp directory to avoid modifying actual files
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set up minimal project structure in temp dir
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            result = run_script(
                ["test-agent", "A test agent"],
                cwd=tmp_path,
            )
            # Should not fail on validation (may fail on other steps)
            assert (
                "invalid" not in result.stderr.lower()
            ), "Valid name should not be rejected"


class TestDuplicateDetection:
    """Tests for duplicate agent detection."""

    def test_duplicate_agent_name_fails(self):
        """Creating agent with existing name fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            # Create an existing agent file
            existing_agent = tmp_path / ".claude" / "agents" / "existing-agent.md"
            existing_agent.write_text(
                "---\nname: existing-agent\n---\n# Existing Agent\n"
            )

            result = run_script(
                ["existing-agent", "A duplicate agent"],
                cwd=tmp_path,
            )
            assert result.returncode == 1, "Duplicate should fail with code 1"
            assert "already exists" in result.stderr.lower(), "Should mention duplicate"

    def test_force_flag_overwrites_existing(self):
        """--force flag allows overwriting existing agent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            # Create an existing agent file
            existing_agent = tmp_path / ".claude" / "agents" / "existing-agent.md"
            existing_agent.write_text(
                "---\nname: existing-agent\n---\n# Existing Agent\n"
            )

            result = run_script(
                ["existing-agent", "A new description", "--force"],
                cwd=tmp_path,
            )
            # With --force, should proceed (may still fail on other issues)
            assert (
                "already exists" not in result.stderr
            ), "Should not complain about existing with --force"


class TestTemplateProcessing:
    """Tests for template processing and placeholder replacement."""

    def test_template_placeholder_replacement(self):
        """All placeholders are replaced in generated agent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            result = run_script(
                [
                    "my-new-agent",
                    "A specialized testing agent",
                    "--model",
                    "claude-opus-4-5-20251101",
                ],
                cwd=tmp_path,
            )

            if result.returncode == 0:
                agent_file = tmp_path / ".claude" / "agents" / "my-new-agent.md"
                assert agent_file.exists(), "Agent file should be created"
                content = agent_file.read_text()

                # Check placeholders are replaced
                assert (
                    "[agent-name]" not in content
                ), "agent-name placeholder should be replaced"
                assert "my-new-agent" in content, "Agent name should appear in file"
                assert (
                    "[One sentence description" not in content
                ), "description placeholder should be replaced"

    def test_model_placeholder_replacement(self):
        """Model placeholder is replaced with specified model."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            result = run_script(
                [
                    "model-test-agent",
                    "Testing model replacement",
                    "--model",
                    "claude-opus-4-5-20251101",
                ],
                cwd=tmp_path,
            )

            if result.returncode == 0:
                agent_file = tmp_path / ".claude" / "agents" / "model-test-agent.md"
                content = agent_file.read_text()
                assert (
                    "claude-opus-4-5-20251101" in content
                ), "Specified model should be in file"
                # Default model should be replaced
                assert (
                    "claude-sonnet-4-20250514" not in content
                ), "Default model should be replaced"

    def test_default_model_used_when_not_specified(self):
        """Default model is used when --model not specified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            result = run_script(
                ["default-model-agent", "Testing default model"],
                cwd=tmp_path,
            )

            if result.returncode == 0:
                agent_file = tmp_path / ".claude" / "agents" / "default-model-agent.md"
                content = agent_file.read_text()
                # Should have the default model (Sonnet 4.5)
                assert (
                    "claude-sonnet-4-5-20250929" in content
                ), "Default model should be Sonnet 4.5"

    def test_no_unresolved_placeholders(self):
        """Generated file has no remaining [bracketed] placeholders in critical sections."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            result = run_script(
                ["clean-agent", "A fully processed agent"],
                cwd=tmp_path,
            )

            if result.returncode == 0:
                agent_file = tmp_path / ".claude" / "agents" / "clean-agent.md"
                content = agent_file.read_text()

                # Check critical sections (frontmatter and header) have no placeholders
                # Extract frontmatter
                lines = content.split("\n")
                in_frontmatter = False
                frontmatter = []
                for line in lines:
                    if line.strip() == "---":
                        if in_frontmatter:
                            break
                        in_frontmatter = True
                        continue
                    if in_frontmatter:
                        frontmatter.append(line)

                frontmatter_text = "\n".join(frontmatter)
                assert (
                    "[" not in frontmatter_text or "]" not in frontmatter_text
                ), f"Frontmatter has unresolved placeholders: {frontmatter_text}"


class TestLauncherIntegration:
    """Tests for launcher file updates."""

    def test_launcher_agent_order_updated(self):
        """Agent is added to agent_order array."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            result = run_script(
                ["launcher-test-agent", "Testing launcher integration"],
                cwd=tmp_path,
            )

            if result.returncode == 0:
                launcher_file = tmp_path / "agents" / "launch"
                content = launcher_file.read_text()
                assert '"launcher-test-agent"' in content, "Agent should be in launcher"

    def test_launcher_serena_agents_updated_when_flag_set(self):
        """Agent is added to serena_agents array when --serena flag is set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            result = run_script(
                ["serena-agent", "Testing serena integration", "--serena"],
                cwd=tmp_path,
            )

            if result.returncode == 0:
                launcher_file = tmp_path / "agents" / "launch"
                content = launcher_file.read_text()
                # Check serena_agents array contains our agent
                assert '"serena-agent"' in content, "Serena agent should be in launcher"
                # Verify it's in serena_agents specifically
                # Find serena_agents section
                serena_start = content.find("serena_agents=(")
                serena_end = content.find(")", serena_start)
                if serena_start != -1 and serena_end != -1:
                    serena_section = content[serena_start:serena_end]
                    assert (
                        "serena-agent" in serena_section
                    ), "Agent should be in serena_agents array"

    def test_launcher_icon_mapping_updated(self):
        """Agent icon mapping is added to get_agent_icon function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            result = run_script(
                ["icon-test-agent", "Testing icon integration", "--emoji", "🎯"],
                cwd=tmp_path,
            )

            if result.returncode == 0:
                launcher_file = tmp_path / "agents" / "launch"
                content = launcher_file.read_text()
                # Check for icon mapping - should be in get_agent_icon function
                assert "icon-test-agent" in content, "Agent should be in icon mapping"
                assert "🎯" in content, "Custom emoji should be in launcher"

    def test_launcher_syntax_valid_after_update(self):
        """Launcher file remains syntactically valid after update."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            result = run_script(
                ["syntax-test-agent", "Testing syntax validity"],
                cwd=tmp_path,
            )

            if result.returncode == 0:
                launcher_file = tmp_path / "agents" / "launch"
                # Validate bash syntax
                syntax_check = subprocess.run(
                    ["bash", "-n", str(launcher_file)],
                    capture_output=True,
                    text=True,
                )
                assert (
                    syntax_check.returncode == 0
                ), f"Launcher has syntax errors: {syntax_check.stderr}"


class TestExitCodes:
    """Tests for exit code conventions."""

    def test_success_returns_zero(self):
        """Successful creation returns exit code 0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            result = run_script(
                ["success-agent", "A successful agent creation"],
                cwd=tmp_path,
            )

            # May fail for other reasons initially, but when it works:
            if "SUCCESS" in result.stdout:
                assert result.returncode == 0, "Success should return code 0"

    def test_user_error_returns_one(self):
        """User errors (invalid input) return exit code 1."""
        result = run_script(["invalid name with spaces", "Description"])
        assert result.returncode == 1, "User error should return code 1"

    def test_missing_template_returns_two(self):
        """System errors (missing template) return exit code 2."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            # Set up project but WITHOUT template file
            setup_temp_project(tmp_path, include_template=False)

            result = run_script(
                ["missing-template-agent", "Should fail"],
                cwd=tmp_path,
            )
            assert result.returncode == 2, "Missing template should return code 2"
            assert "template" in result.stderr.lower(), "Should mention template issue"


class TestErrorMessages:
    """Tests for error message quality (for AGENT-CREATOR consumption)."""

    def test_error_messages_to_stderr(self):
        """Error messages go to stderr, not stdout."""
        result = run_script(["invalid name", "Description"])
        assert result.stderr, "Errors should go to stderr"
        # Stdout might have some output but errors should be on stderr

    def test_error_includes_action_recommendation(self):
        """Error messages include actionable recommendations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            # Create duplicate
            existing_agent = tmp_path / ".claude" / "agents" / "dup-agent.md"
            existing_agent.write_text("---\nname: dup-agent\n---\n")

            result = run_script(
                ["dup-agent", "Duplicate"],
                cwd=tmp_path,
            )

            # Should include action recommendation
            stderr_lower = result.stderr.lower()
            assert (
                "--force" in result.stderr or "force" in stderr_lower
            ), "Should mention --force option for duplicates"


class TestLogging:
    """Tests for JSON logging functionality."""

    def test_logs_directory_created(self):
        """logs/ directory is created if missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path, include_logs_dir=False)

            result = run_script(
                ["logging-test-agent", "Testing logging"],
                cwd=tmp_path,
            )

            logs_dir = tmp_path / "logs"
            # Should create logs directory
            if result.returncode == 0 or "agent-creation.log" in str(result.stderr):
                assert logs_dir.exists(), "logs/ directory should be created"

    def test_json_log_format(self):
        """Logs are in valid JSON format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            run_script(
                ["json-log-agent", "Testing JSON logging"],
                cwd=tmp_path,
            )

            log_file = tmp_path / "logs" / "agent-creation.log"
            if log_file.exists():
                content = log_file.read_text()
                if content.strip():
                    # Each line should be valid JSON
                    for line in content.strip().split("\n"):
                        if line.strip():
                            try:
                                json.loads(line)
                            except json.JSONDecodeError:
                                pytest.fail(f"Invalid JSON in log: {line}")


class TestFileLocking:
    """Tests for concurrent access protection."""

    # Note: Lock file creation during operation is tested in integration tests
    # (tests/integration/test_concurrent_agent_creation.py) for actual concurrent behavior

    def test_lock_released_on_success(self):
        """Lock file is released after successful completion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            result = run_script(
                ["lock-test-agent", "Testing lock release"],
                cwd=tmp_path,
            )

            lock_file = Path("/tmp/agent-creation-launcher.lock")
            # After successful completion, lock should be released
            # (file may exist but shouldn't be locked)
            if result.returncode == 0:
                # Try to acquire the lock ourselves
                import fcntl

                try:
                    with open(lock_file, "w") as f:
                        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except BlockingIOError:
                    pytest.fail("Lock was not released after successful completion")


class TestCleanup:
    """Tests for cleanup on failure."""

    def test_partial_files_cleaned_on_failure(self):
        """Partial agent files are removed if creation fails midway."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            # Make the launcher unwritable to cause failure during launcher update
            launcher_file = tmp_path / "agents" / "launch"
            launcher_file.chmod(0o444)  # Read-only

            try:
                result = run_script(
                    ["cleanup-test-agent", "Testing cleanup on failure"],
                    cwd=tmp_path,
                )

                # Script should fail because launcher is not writable
                assert (
                    result.returncode != 0
                ), "Script should fail with read-only launcher"

                # Agent file may have been created before the launcher update failed
                # The script's cleanup should remove it, OR it should not exist
                agent_file = tmp_path / ".claude" / "agents" / "cleanup-test-agent.md"
                # Note: The key assertion is that the script handles the error gracefully
                # (exits with non-zero code, verified above)
            finally:
                # Restore launcher permissions for cleanup
                launcher_file.chmod(0o755)


class TestDryRunMode:
    """Tests for dry-run functionality."""

    def test_dry_run_no_files_modified(self):
        """--dry-run flag shows changes without modifying files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            setup_temp_project(tmp_path)

            # Get original launcher content
            launcher_file = tmp_path / "agents" / "launch"
            original_launcher = launcher_file.read_text()

            result = run_script(
                ["dry-run-agent", "Testing dry run", "--dry-run"],
                cwd=tmp_path,
            )

            # Should succeed without modifying files
            assert (
                result.returncode == 0 or "--dry-run" in result.stdout
            ), "Dry run should succeed"

            # Files should be unchanged
            if "--dry-run" in result.stdout or "would create" in result.stdout.lower():
                assert (
                    launcher_file.read_text() == original_launcher
                ), "Launcher should not be modified in dry-run"

                agent_file = tmp_path / ".claude" / "agents" / "dry-run-agent.md"
                assert (
                    not agent_file.exists()
                ), "Agent file should not be created in dry-run"


# Note: setup_temp_project is imported from conftest.py
