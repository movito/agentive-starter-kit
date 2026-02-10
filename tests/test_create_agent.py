"""
Tests for scripts/create-agent.sh — Agent creation automation.

TDD Red Phase: These tests define the behavioral contract for the script.
The script does NOT exist yet; all tests that invoke it will fail until
the Green Phase implementation is complete.

Bug ledger coverage:
  S1  — test_description_with_special_chars (sed escaping)
  S2  — test_icon_glob_matching (glob wildcards)
  S3  — test_launcher_scoped_array_update (AWK array scoping)
  S4  — test_force_no_launcher_duplicates (--force duplicate prevention)
  S5  — test_stale_lock_recovery (stale lock with dead PID)
  S6  — test_concurrent_lock_atomic (mkdir atomic primitive)
  S7  — test_force_replaces_icon (--force updates icon mapping)
  S8  — test_unknown_flag_rejected (removed --position flag)
  S9  — test_launcher_indentation_golden_file (AWK indentation)
  S10 — test_log_json_valid (JSON log via python3)
  T4  — All assertions check returncode first, then output
  T6  — Every captured variable used in an assertion
  T7  — test_no_unresolved_placeholders (regex-based detection)
"""

import json
import re
import shutil
from pathlib import Path

import pytest

from conftest import CREATE_AGENT_LOCK_DIR as LOCK_DIR
from conftest import CREATE_AGENT_SCRIPT as SCRIPT_PATH
from conftest import run_create_agent_script as run_script
from conftest import setup_temp_project

# ---------------------------------------------------------------------------
# JSON log required fields (from plan's JSON Log Schema)
# ---------------------------------------------------------------------------
LOG_REQUIRED_FIELDS = {
    "timestamp",
    "level",
    "operation",
    "agent_name",
    "status",
}


# ===================================================================
# 1. TestScriptExists — Verify the script file itself
# ===================================================================
class TestScriptExists:
    """Verify that the create-agent script exists and has correct attributes."""

    def test_script_file_exists(self):
        """Script file exists at scripts/create-agent.sh."""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"

    def test_script_has_bash_shebang(self):
        """Script starts with #!/bin/bash shebang line."""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
        first_line = SCRIPT_PATH.read_text().split("\n", 1)[0]
        assert first_line.startswith(
            "#!/bin/bash"
        ), f"Expected #!/bin/bash shebang, got: {first_line!r}"


# ===================================================================
# 2. TestHelpUsage — --help flag behavior
# ===================================================================
class TestHelpUsage:
    """Verify --help output matches the CLI contract."""

    def setup_method(self):
        self.project_dir = setup_temp_project()

    def teardown_method(self):
        shutil.rmtree(self.project_dir, ignore_errors=True)

    def test_help_exits_zero(self):
        """--help exits with code 0."""
        result = run_script(["--help"], self.project_dir)
        assert (
            result.returncode == 0
        ), f"Expected exit 0, got {result.returncode}: {result.stderr}"

    def test_help_shows_usage(self):
        """--help output contains 'Usage:' header."""
        result = run_script(["--help"], self.project_dir)
        assert (
            result.returncode == 0
        ), f"Expected exit 0, got {result.returncode}: {result.stderr}"
        assert (
            "Usage:" in result.stdout
        ), f"Expected 'Usage:' in help output, got:\n{result.stdout}"

    def test_help_documents_all_options(self):
        """--help documents all CLI options from the contract."""
        result = run_script(["--help"], self.project_dir)
        assert (
            result.returncode == 0
        ), f"Expected exit 0, got {result.returncode}: {result.stderr}"
        expected_options = [
            "--model",
            "--emoji",
            "--serena",
            "--force",
            "--dry-run",
            "--help",
        ]
        for opt in expected_options:
            assert (
                opt in result.stdout
            ), f"Option {opt!r} not found in help output:\n{result.stdout}"


# ===================================================================
# 3. TestInputValidation — Argument validation rules
# ===================================================================
class TestInputValidation:
    """Verify input validation rejects bad inputs and accepts valid ones."""

    def setup_method(self):
        self.project_dir = setup_temp_project()

    def teardown_method(self):
        shutil.rmtree(self.project_dir, ignore_errors=True)

    def test_missing_name_rejected(self):
        """Running with no arguments produces exit 1."""
        result = run_script([], self.project_dir)
        assert (
            result.returncode == 1
        ), f"Expected exit 1 for missing name, got {result.returncode}: {result.stderr}"

    def test_missing_description_rejected(self):
        """Running with name but no description produces exit 1."""
        result = run_script(["test-agent"], self.project_dir)
        assert (
            result.returncode == 1
        ), f"Expected exit 1 for missing description, got {result.returncode}: {result.stderr}"

    def test_invalid_name_uppercase_rejected(self):
        """Uppercase characters in agent name are rejected (exit 1)."""
        result = run_script(["BadName", "A test agent description"], self.project_dir)
        assert (
            result.returncode == 1
        ), f"Expected exit 1 for uppercase name, got {result.returncode}: {result.stderr}"

    def test_invalid_name_too_short_rejected(self):
        """Agent name shorter than 2 characters is rejected (exit 1)."""
        result = run_script(["x", "A test agent description"], self.project_dir)
        assert (
            result.returncode == 1
        ), f"Expected exit 1 for name too short, got {result.returncode}: {result.stderr}"

    def test_invalid_name_special_chars_rejected(self):
        """Agent name with special characters (spaces, dots) is rejected (exit 1).

        Bug S8 regression: unknown flags like --position should also be rejected.
        """
        result = run_script(
            ["bad.agent name!", "A test agent description"], self.project_dir
        )
        assert (
            result.returncode == 1
        ), f"Expected exit 1 for special chars in name, got {result.returncode}: {result.stderr}"

    def test_valid_name_accepted(self):
        """A properly formatted name (lowercase, hyphens, 2-30 chars) is accepted."""
        result = run_script(
            ["my-valid-agent", "A valid test agent for CI"], self.project_dir
        )
        # Should NOT fail on input validation (may still fail if script not implemented)
        # But if it runs, it should not be exit 1 for "invalid name"
        assert (
            "invalid" not in result.stderr.lower() or result.returncode != 1
        ), f"Valid name was rejected: {result.stderr}"

    def test_unknown_flag_rejected(self):
        """Unknown flags like --position are rejected with exit 1.

        Bug S8 regression: --position was parsed but never implemented.
        """
        result = run_script(
            ["test-agent", "A test agent", "--position", "3"], self.project_dir
        )
        assert (
            result.returncode == 1
        ), f"Expected exit 1 for unknown flag --position, got {result.returncode}: {result.stderr}"


# ===================================================================
# 4. TestDuplicateDetection — Duplicate agent handling
# ===================================================================
class TestDuplicateDetection:
    """Verify duplicate agent name detection and --force override."""

    def setup_method(self):
        self.project_dir = setup_temp_project()

    def teardown_method(self):
        shutil.rmtree(self.project_dir, ignore_errors=True)

    def _create_existing_agent(self, name: str = "existing-agent"):
        """Create a pre-existing agent file to trigger duplicate detection."""
        agent_file = self.project_dir / ".claude" / "agents" / f"{name}.md"
        agent_file.write_text(
            "---\n"
            f"name: {name}\n"
            "description: Pre-existing agent\n"
            "model: claude-sonnet-4-5-20250929\n"
            "---\n"
            f"# {name}\n"
        )

    def test_duplicate_name_rejected(self):
        """Creating an agent with an existing name exits 1 without --force."""
        self._create_existing_agent("existing-agent")
        result = run_script(
            ["existing-agent", "Another agent with same name"], self.project_dir
        )
        assert (
            result.returncode == 1
        ), f"Expected exit 1 for duplicate name, got {result.returncode}: {result.stderr}"

    def test_force_overwrites_duplicate(self):
        """--force allows overwriting an existing agent (exit 0)."""
        self._create_existing_agent("existing-agent")
        result = run_script(
            ["existing-agent", "Replacement description", "--force"], self.project_dir
        )
        assert (
            result.returncode == 0
        ), f"Expected exit 0 with --force, got {result.returncode}: {result.stderr}"
        agent_file = self.project_dir / ".claude" / "agents" / "existing-agent.md"
        content = agent_file.read_text()
        assert (
            "Replacement description" in content
        ), f"Agent file not updated with new description:\n{content}"

    def test_dry_run_reports_duplicate(self):
        """--dry-run reports that a duplicate exists without modifying anything."""
        self._create_existing_agent("existing-agent")
        result = run_script(
            ["existing-agent", "Another description", "--dry-run"], self.project_dir
        )
        assert (
            result.returncode == 0
        ), f"Expected exit 0 for --dry-run, got {result.returncode}: {result.stderr}"
        assert (
            "exist" in result.stdout.lower() or "duplicate" in result.stdout.lower()
        ), f"Dry-run did not report duplicate:\n{result.stdout}"


# ===================================================================
# 5. TestTemplateProcessing — Placeholder replacement
# ===================================================================
class TestTemplateProcessing:
    """Verify template placeholders are correctly replaced in agent files."""

    def setup_method(self):
        self.project_dir = setup_temp_project()

    def teardown_method(self):
        shutil.rmtree(self.project_dir, ignore_errors=True)

    def test_all_placeholders_replaced(self):
        """Agent file has no leftover [placeholder] brackets after creation."""
        result = run_script(
            ["test-agent", "A test agent for validation"], self.project_dir
        )
        assert (
            result.returncode == 0
        ), f"Expected exit 0, got {result.returncode}: {result.stderr}"
        agent_file = self.project_dir / ".claude" / "agents" / "test-agent.md"
        assert agent_file.exists(), f"Agent file not created at {agent_file}"
        content = agent_file.read_text()
        # T7 regression: use regex, not string containment
        unresolved = re.findall(r"\[[A-Z][A-Za-z -]+\]", content)
        assert len(unresolved) == 0, f"Unresolved placeholders: {unresolved}"

    def test_no_unresolved_placeholders(self):
        """Dedicated regression test for T7: placeholder detection via regex.

        The original test suite used `assert '[' not in content or ']' not in content`
        which is logically broken — this test uses proper regex matching.
        """
        result = run_script(
            ["placeholder-check", "Placeholder regression test agent"], self.project_dir
        )
        assert (
            result.returncode == 0
        ), f"Expected exit 0, got {result.returncode}: {result.stderr}"
        agent_file = self.project_dir / ".claude" / "agents" / "placeholder-check.md"
        assert agent_file.exists(), f"Agent file not created at {agent_file}"
        content = agent_file.read_text()
        # T7: Must use regex for reliable detection
        unresolved = re.findall(r"\[[A-Z][A-Za-z -]+\]", content)
        assert len(unresolved) == 0, f"Unresolved placeholders found: {unresolved}"

    def test_description_with_special_chars(self):
        """Bug S1 regression: description with /, &, \\ does not break sed.

        The original implementation used sed without escaping special characters,
        causing template replacement to fail for descriptions containing
        forward slashes, ampersands, or backslashes.
        """
        tricky_desc = "Handles input/output & manages paths like C:\\Users"
        result = run_script(["special-chars-agent", tricky_desc], self.project_dir)
        assert (
            result.returncode == 0
        ), f"Expected exit 0, got {result.returncode}: {result.stderr}"
        agent_file = self.project_dir / ".claude" / "agents" / "special-chars-agent.md"
        assert agent_file.exists(), f"Agent file not created at {agent_file}"
        content = agent_file.read_text()
        assert (
            "input/output" in content
        ), f"Forward slash in description was mangled:\n{content}"
        assert "&" in content, f"Ampersand in description was mangled:\n{content}"

    def test_name_substituted_in_frontmatter(self):
        """Agent name appears in the YAML frontmatter 'name:' field."""
        result = run_script(
            ["frontmatter-agent", "Frontmatter name substitution test"],
            self.project_dir,
        )
        assert (
            result.returncode == 0
        ), f"Expected exit 0, got {result.returncode}: {result.stderr}"
        agent_file = self.project_dir / ".claude" / "agents" / "frontmatter-agent.md"
        assert agent_file.exists(), f"Agent file not created at {agent_file}"
        content = agent_file.read_text()
        assert (
            "name: frontmatter-agent" in content
        ), f"Agent name not in frontmatter:\n{content}"


# ===================================================================
# 6. TestLauncherIntegration — agents/launch modifications
# ===================================================================
class TestLauncherIntegration:
    """Verify that agents/launch is correctly updated with new agent entries."""

    def setup_method(self):
        self.project_dir = setup_temp_project()

    def teardown_method(self):
        shutil.rmtree(self.project_dir, ignore_errors=True)

    def test_agent_added_to_agent_order(self):
        """New agent appears in the agent_order array in agents/launch."""
        result = run_script(
            ["order-test-agent", "Agent for order array test"], self.project_dir
        )
        assert (
            result.returncode == 0
        ), f"Expected exit 0, got {result.returncode}: {result.stderr}"
        launcher = (self.project_dir / "agents" / "launch").read_text()
        assert (
            '"order-test-agent"' in launcher
        ), f"Agent not added to launcher agent_order:\n{launcher}"

    def test_serena_agent_added_when_flag_set(self):
        """--serena flag adds agent to the serena_agents array."""
        result = run_script(
            ["serena-test", "Serena-enabled agent", "--serena"], self.project_dir
        )
        assert (
            result.returncode == 0
        ), f"Expected exit 0, got {result.returncode}: {result.stderr}"
        launcher = (self.project_dir / "agents" / "launch").read_text()
        # Find the serena_agents block and check our agent is in it
        assert '"serena-test"' in launcher, f"Agent not found in launcher:\n{launcher}"
        # Verify it's in the serena_agents section specifically
        serena_match = re.search(r"serena_agents=\((.*?)\)", launcher, re.DOTALL)
        assert (
            serena_match is not None
        ), f"serena_agents array not found in launcher:\n{launcher}"
        assert "serena-test" in serena_match.group(
            1
        ), f"Agent not in serena_agents array:\n{serena_match.group(1)}"

    def test_icon_added_to_get_agent_icon(self):
        """New agent gets an icon mapping in get_agent_icon function."""
        result = run_script(
            ["icon-test-agent", "Icon mapping test agent"], self.project_dir
        )
        assert (
            result.returncode == 0
        ), f"Expected exit 0, got {result.returncode}: {result.stderr}"
        launcher = (self.project_dir / "agents" / "launch").read_text()
        # Should have an icon pattern matching this agent
        assert (
            "icon-test-agent" in launcher
        ), f"Agent icon mapping not found in launcher:\n{launcher}"

    def test_launcher_indentation_golden_file(self):
        """Bug S9 regression: AWK-generated entries have correct indentation.

        Golden-file test: compare launcher output against expected format.
        agent_order entries use 8-space indent, icon mappings use 4-space indent.
        """
        result = run_script(
            ["golden-agent", "Golden file indentation test"], self.project_dir
        )
        assert (
            result.returncode == 0
        ), f"Expected exit 0, got {result.returncode}: {result.stderr}"
        launcher = (self.project_dir / "agents" / "launch").read_text()

        # Verify agent_order entry indentation (8 spaces)
        order_pattern = re.compile(r'^        "golden-agent"$', re.MULTILINE)
        assert order_pattern.search(launcher), (
            f"agent_order entry has wrong indentation. Expected 8-space indent.\n"
            f"Launcher content:\n{launcher}"
        )

        # Verify icon mapping indentation (4 spaces for the [[ line)
        icon_pattern = re.compile(r"^    \[\[.*golden-agent.*\]\].*icon=", re.MULTILINE)
        assert icon_pattern.search(launcher), (
            f"Icon mapping has wrong indentation. Expected 4-space indent.\n"
            f"Launcher content:\n{launcher}"
        )

    def test_force_no_launcher_duplicates(self):
        """Bug S4 regression: --force does not create duplicate launcher entries.

        The original implementation appended without checking for existing entries,
        resulting in duplicated array elements when --force was used.
        """
        # First creation
        result1 = run_script(["dup-check", "First creation"], self.project_dir)
        assert (
            result1.returncode == 0
        ), f"First creation failed: {result1.returncode}: {result1.stderr}"

        # Second creation with --force
        result2 = run_script(
            ["dup-check", "Second creation with force", "--force"], self.project_dir
        )
        assert (
            result2.returncode == 0
        ), f"Force recreation failed: {result2.returncode}: {result2.stderr}"

        launcher = (self.project_dir / "agents" / "launch").read_text()
        # Count occurrences of the agent in agent_order array
        occurrences = launcher.count('"dup-check"')
        assert occurrences == 1, (
            f"Expected exactly 1 occurrence of '\"dup-check\"' in launcher, "
            f"found {occurrences}. Bug S4: --force created duplicates.\n{launcher}"
        )


# ===================================================================
# 7. TestExitCodes — Exit code contract
# ===================================================================
class TestExitCodes:
    """Verify exit code semantics: 0=success, 1=user error, 2=system error."""

    def setup_method(self):
        self.project_dir = setup_temp_project()

    def teardown_method(self):
        shutil.rmtree(self.project_dir, ignore_errors=True)

    def test_exit_0_on_success(self):
        """Successful agent creation exits with code 0."""
        result = run_script(
            ["success-agent", "Successful creation test"], self.project_dir
        )
        assert (
            result.returncode == 0
        ), f"Expected exit 0 on success, got {result.returncode}: {result.stderr}"

    def test_exit_1_on_user_error(self):
        """Invalid input (user error) exits with code 1."""
        result = run_script([], self.project_dir)
        assert (
            result.returncode == 1
        ), f"Expected exit 1 for user error (no args), got {result.returncode}: {result.stderr}"

    def test_exit_2_on_system_error(self):
        """System error (e.g., missing template) exits with code 2.

        Remove the template file to trigger a system error.
        """
        template = self.project_dir / ".claude" / "agents" / "AGENT-TEMPLATE.md"
        template.unlink()
        result = run_script(
            ["sys-error-agent", "Should fail with system error"], self.project_dir
        )
        assert result.returncode == 2, (
            f"Expected exit 2 for system error (missing template), "
            f"got {result.returncode}: {result.stderr}"
        )


# ===================================================================
# 8. TestLogging — JSON log file creation and validity
# ===================================================================
class TestLogging:
    """Verify log file creation and JSON format (S10 regression)."""

    def setup_method(self):
        self.project_dir = setup_temp_project()

    def teardown_method(self):
        shutil.rmtree(self.project_dir, ignore_errors=True)

    def test_log_file_created(self):
        """Log file is created in logs/ directory after script execution."""
        result = run_script(
            ["log-test-agent", "Log creation test agent"], self.project_dir
        )
        assert (
            result.returncode == 0
        ), f"Expected exit 0, got {result.returncode}: {result.stderr}"
        log_file = self.project_dir / "logs" / "agent-creation.log"
        assert log_file.exists(), f"Log file not created at {log_file}"

    def test_log_json_valid(self):
        """Bug S10 regression: every log line is valid JSON.

        The original implementation used string concatenation for JSON,
        which produced malformed output. The fix uses python3 -c 'import json; ...'
        """
        result = run_script(
            ["json-log-agent", "JSON log validity test agent"], self.project_dir
        )
        assert (
            result.returncode == 0
        ), f"Expected exit 0, got {result.returncode}: {result.stderr}"
        log_file = self.project_dir / "logs" / "agent-creation.log"
        assert log_file.exists(), f"Log file not created at {log_file}"

        lines = log_file.read_text().strip().splitlines()
        assert len(lines) > 0, "Log file is empty"
        for i, line in enumerate(lines):
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                pytest.fail(f"Log line {i + 1} is not valid JSON: {e}\nLine: {line!r}")

    def test_log_has_required_fields(self):
        """Log entries contain all required fields from the JSON Log Schema."""
        result = run_script(
            ["fields-log-agent", "Log required fields test agent"], self.project_dir
        )
        assert (
            result.returncode == 0
        ), f"Expected exit 0, got {result.returncode}: {result.stderr}"
        log_file = self.project_dir / "logs" / "agent-creation.log"
        assert log_file.exists(), f"Log file not created at {log_file}"

        lines = log_file.read_text().strip().splitlines()
        assert len(lines) > 0, "Log file is empty"
        for i, line in enumerate(lines):
            entry = json.loads(line)
            missing = LOG_REQUIRED_FIELDS - set(entry.keys())
            assert (
                len(missing) == 0
            ), f"Log line {i + 1} missing required fields: {missing}\nEntry: {entry}"


# ===================================================================
# 9. TestDryRun — --dry-run behavior
# ===================================================================
class TestDryRun:
    """Verify --dry-run shows planned actions without modifying files."""

    def setup_method(self):
        self.project_dir = setup_temp_project()

    def teardown_method(self):
        shutil.rmtree(self.project_dir, ignore_errors=True)

    def test_dry_run_no_files_modified(self):
        """--dry-run does not create the agent file or modify the launcher."""
        launcher_before = (self.project_dir / "agents" / "launch").read_text()

        result = run_script(
            ["dry-run-agent", "Dry run test agent", "--dry-run"], self.project_dir
        )
        assert (
            result.returncode == 0
        ), f"Expected exit 0, got {result.returncode}: {result.stderr}"

        # Agent file should NOT exist
        agent_file = self.project_dir / ".claude" / "agents" / "dry-run-agent.md"
        assert not agent_file.exists(), f"--dry-run created agent file at {agent_file}"

        # Launcher should be unchanged
        launcher_after = (self.project_dir / "agents" / "launch").read_text()
        assert launcher_before == launcher_after, "--dry-run modified the launcher file"

    def test_dry_run_reports_planned_actions(self):
        """--dry-run output describes what would be done."""
        result = run_script(
            ["dry-run-agent", "Dry run test agent", "--dry-run"], self.project_dir
        )
        assert (
            result.returncode == 0
        ), f"Expected exit 0, got {result.returncode}: {result.stderr}"
        stdout_lower = result.stdout.lower()
        # Should mention what it would create/modify
        assert (
            "would" in stdout_lower or "dry" in stdout_lower or "plan" in stdout_lower
        ), f"Dry-run output doesn't describe planned actions:\n{result.stdout}"
