"""
Tests for scripts/project CLI commands.

Focus: install-evaluators command with mocked subprocess calls.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from conftest import MockVersionInfo

# Load the project script as a module
_script_path = Path(__file__).parent.parent / "scripts" / "project"
_spec = importlib.util.spec_from_loader("project_script", loader=None)
_project_module = importlib.util.module_from_spec(_spec)

# Read and execute the script to get the functions
# Inject __file__ so Path(__file__) works in cmd_setup
with open(_script_path) as f:
    _project_module.__dict__["__file__"] = str(_script_path)
    exec(f.read(), _project_module.__dict__)


class TestInstallEvaluatorsCommand:
    """Tests for install-evaluators command."""

    @pytest.fixture
    def mock_project_dir(self, tmp_path):
        """Create a temporary project directory structure."""
        evaluators_dir = tmp_path / ".adversarial" / "evaluators"
        evaluators_dir.mkdir(parents=True)
        return tmp_path

    def test_git_not_found(self, mock_project_dir, capsys):
        """Installer fails gracefully when git is not available."""
        cmd_install_evaluators = _project_module.cmd_install_evaluators

        # Mock subprocess.run to simulate git not found
        with patch.object(_project_module, "subprocess") as mock_subprocess:
            mock_subprocess.run.return_value = MagicMock(returncode=1)
            mock_subprocess.TimeoutExpired = subprocess.TimeoutExpired

            with pytest.raises(SystemExit) as exc_info:
                cmd_install_evaluators([], mock_project_dir)

            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Git is required but not found" in captured.out

    def test_already_installed_skips(self, mock_project_dir, capsys):
        """Running twice with same version skips re-install."""
        cmd_install_evaluators = _project_module.cmd_install_evaluators

        # Create .installed-version file
        evaluators_dir = mock_project_dir / ".adversarial" / "evaluators"
        version_file = evaluators_dir / ".installed-version"
        version_file.write_text("v0.2.2 (abc12345)\n")

        # Mock subprocess.run - git check should succeed
        with patch.object(_project_module, "subprocess") as mock_subprocess:
            mock_subprocess.run.return_value = MagicMock(returncode=0)
            mock_subprocess.TimeoutExpired = subprocess.TimeoutExpired

            # Should not raise, just return early
            cmd_install_evaluators([], mock_project_dir)

        captured = capsys.readouterr()
        assert "already installed" in captured.out
        assert "Use --force to reinstall" in captured.out

    def test_force_reinstalls(self, mock_project_dir, capsys):
        """--force flag triggers reinstall even if version matches."""
        cmd_install_evaluators = _project_module.cmd_install_evaluators

        # Create .installed-version file
        evaluators_dir = mock_project_dir / ".adversarial" / "evaluators"
        version_file = evaluators_dir / ".installed-version"
        version_file.write_text("v0.2.2 (abc12345)\n")

        # Mock subprocess.run for git check and clone
        with patch.object(_project_module, "subprocess") as mock_subprocess:
            mock_subprocess.TimeoutExpired = subprocess.TimeoutExpired
            # First call: git --version (success)
            # Second call: git clone (fail - we don't have a real repo)
            mock_subprocess.run.side_effect = [
                MagicMock(returncode=0),  # git --version
                MagicMock(returncode=1, stderr="not found"),  # git clone fails
            ]

            with pytest.raises(SystemExit):
                cmd_install_evaluators(["--force"], mock_project_dir)

        captured = capsys.readouterr()
        # Should NOT show "already installed" message
        assert "already installed" not in captured.out
        # Should attempt to clone (even though it fails in mock)
        assert "Cloning evaluator library" in captured.out

    def test_ref_flag_overrides_version(self, mock_project_dir, capsys):
        """--ref <tag> uses specified version instead of default."""
        cmd_install_evaluators = _project_module.cmd_install_evaluators

        custom_version = "v0.3.0"

        # Mock subprocess.run - should fail clone since no real repo
        with patch.object(_project_module, "subprocess") as mock_subprocess:
            mock_subprocess.TimeoutExpired = subprocess.TimeoutExpired
            mock_subprocess.run.side_effect = [
                MagicMock(returncode=0),  # git --version
                MagicMock(returncode=1, stderr="not found"),  # git clone fails
            ]

            with pytest.raises(SystemExit):
                cmd_install_evaluators(["--ref", custom_version], mock_project_dir)

        captured = capsys.readouterr()
        # Should show the custom version in output
        assert custom_version in captured.out

    def test_clone_timeout_handled(self, mock_project_dir, capsys):
        """Clone timeout is handled gracefully."""
        cmd_install_evaluators = _project_module.cmd_install_evaluators

        with patch.object(_project_module, "subprocess") as mock_subprocess:
            mock_subprocess.TimeoutExpired = subprocess.TimeoutExpired
            mock_subprocess.run.side_effect = [
                MagicMock(returncode=0),  # git --version
                subprocess.TimeoutExpired(cmd="git clone", timeout=60),  # timeout
            ]

            with pytest.raises(SystemExit) as exc_info:
                cmd_install_evaluators([], mock_project_dir)

            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "timed out" in captured.out

    def test_network_error_handled(self, mock_project_dir, capsys):
        """Network error during clone is handled gracefully."""
        cmd_install_evaluators = _project_module.cmd_install_evaluators

        with patch.object(_project_module, "subprocess") as mock_subprocess:
            mock_subprocess.TimeoutExpired = subprocess.TimeoutExpired
            mock_subprocess.run.side_effect = [
                MagicMock(returncode=0),  # git --version
                MagicMock(
                    returncode=1, stderr="Could not resolve host"
                ),  # network error
            ]

            with pytest.raises(SystemExit) as exc_info:
                cmd_install_evaluators([], mock_project_dir)

            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Network error" in captured.out


class TestSetupNextSteps:
    """Tests for the 'Next Steps' section in setup output."""

    @pytest.fixture
    def mock_project_dir(self, tmp_path):
        """Create a temporary project directory structure."""
        return tmp_path

    def test_setup_shows_next_steps_when_not_in_venv(self, capsys, monkeypatch):
        """Setup should show 'Next step' with activate command when not in venv."""
        cmd_setup = _project_module.cmd_setup

        # Ensure VIRTUAL_ENV is not set
        monkeypatch.delenv("VIRTUAL_ENV", raising=False)

        # Mock the setup to succeed and only run the final output
        mock_version = MockVersionInfo(3, 12, 0)
        with patch.object(_project_module.sys, "version_info", mock_version):
            with patch.object(_project_module, "Path") as mock_path:
                mock_venv = MagicMock()
                mock_venv.exists.return_value = True
                mock_venv.__truediv__ = lambda self, x: mock_venv
                mock_venv.__str__ = lambda self: "/fake/.venv"
                mock_path.return_value.__truediv__ = lambda self, x: mock_venv
                mock_path.return_value.resolve.return_value.parent.parent = Path(
                    "/fake"
                )

                with patch.object(_project_module, "subprocess") as mock_subprocess:
                    mock_subprocess.run.return_value = MagicMock(returncode=0)

                    try:
                        cmd_setup([])
                    except SystemExit:
                        pass

        captured = capsys.readouterr()
        assert "Next step" in captured.out
        assert "activate" in captured.out
        assert "Setup complete!" in captured.out

    def test_setup_detects_active_venv(self, capsys, monkeypatch):
        """Setup should detect if already in venv and show different message."""
        cmd_setup = _project_module.cmd_setup

        # Set VIRTUAL_ENV to simulate being in an active venv
        monkeypatch.setenv("VIRTUAL_ENV", "/some/path/.venv")

        mock_version = MockVersionInfo(3, 12, 0)
        with patch.object(_project_module.sys, "version_info", mock_version):
            with patch.object(_project_module, "Path") as mock_path:
                mock_venv = MagicMock()
                mock_venv.exists.return_value = True
                mock_venv.__truediv__ = lambda self, x: mock_venv
                mock_venv.__str__ = lambda self: "/fake/.venv"
                mock_path.return_value.__truediv__ = lambda self, x: mock_venv
                mock_path.return_value.resolve.return_value.parent.parent = Path(
                    "/fake"
                )

                with patch.object(_project_module, "subprocess") as mock_subprocess:
                    mock_subprocess.run.return_value = MagicMock(returncode=0)

                    try:
                        cmd_setup([])
                    except SystemExit:
                        pass

        captured = capsys.readouterr()
        assert "already in a virtual environment" in captured.out
        # Should NOT show the activation command
        assert "Next step" not in captured.out


class TestGetActivateCommand:
    """Tests for shell-specific activate command detection."""

    def test_default_shell_uses_activate(self, monkeypatch):
        """Default (bash/zsh/sh) uses standard activate script."""
        get_activate_command = _project_module.get_activate_command

        monkeypatch.setenv("SHELL", "/bin/bash")
        result = get_activate_command(Path(".venv"))
        assert "activate" in result
        assert "activate.fish" not in result
        assert "activate.csh" not in result

    def test_fish_shell_uses_activate_fish(self, monkeypatch):
        """Fish shell uses activate.fish script."""
        get_activate_command = _project_module.get_activate_command

        monkeypatch.setenv("SHELL", "/usr/local/bin/fish")
        result = get_activate_command(Path(".venv"))
        assert "activate.fish" in result

    def test_csh_shell_uses_activate_csh(self, monkeypatch):
        """C shell uses activate.csh script."""
        get_activate_command = _project_module.get_activate_command

        monkeypatch.setenv("SHELL", "/bin/csh")
        result = get_activate_command(Path(".venv"))
        assert "activate.csh" in result

    def test_tcsh_shell_uses_activate_csh(self, monkeypatch):
        """Tcsh shell uses activate.csh script."""
        get_activate_command = _project_module.get_activate_command

        monkeypatch.setenv("SHELL", "/bin/tcsh")
        result = get_activate_command(Path(".venv"))
        assert "activate.csh" in result

    def test_no_shell_env_uses_default(self, monkeypatch):
        """Missing SHELL env var falls back to default activate."""
        get_activate_command = _project_module.get_activate_command

        monkeypatch.delenv("SHELL", raising=False)
        result = get_activate_command(Path(".venv"))
        assert "activate" in result
        assert "activate.fish" not in result
        assert "activate.csh" not in result


class TestPythonVersionCheck:
    """Tests for Python version checking in setup command."""

    @pytest.fixture
    def mock_project_dir(self, tmp_path):
        """Create a temporary project directory structure."""
        return tmp_path

    def test_python_too_old_error(self, mock_project_dir, capsys):
        """Python <3.10 shows clear error with upgrade instructions."""
        cmd_setup = _project_module.cmd_setup

        # Mock sys.version_info to simulate Python 3.9
        mock_version = MockVersionInfo(3, 9, 0)
        with patch.object(_project_module.sys, "version_info", mock_version):
            with pytest.raises(SystemExit) as exc_info:
                cmd_setup([])

            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "3.9.0" in captured.out
        assert "too old" in captured.out
        assert "3.10" in captured.out
        # Should include installation options
        assert "pyenv" in captured.out
        assert "brew" in captured.out

    def test_python_too_new_error(self, mock_project_dir, capsys):
        """Python >=3.13 without uv shows clear error with constraint explanation."""
        cmd_setup = _project_module.cmd_setup

        # Mock sys.version_info to simulate Python 3.13
        mock_version = MockVersionInfo(3, 13, 0)
        with patch.object(_project_module.sys, "version_info", mock_version):
            # Mock detect_uv to return False (uv not available)
            with patch.object(_project_module, "detect_uv", return_value=False):
                with pytest.raises(SystemExit) as exc_info:
                    cmd_setup([])

                assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "3.13.0" in captured.out
        assert "not yet supported" in captured.out or "not supported" in captured.out
        # Should explain the constraint source
        assert "aider-chat" in captured.out or "adversarial-workflow" in captured.out
        # Should include remediation options (uv is now primary recommendation)
        assert "uv" in captured.out
        assert "pyenv" in captured.out
        assert "brew" in captured.out

    def test_python_future_version_error(self, mock_project_dir, capsys):
        """Python 3.14+ without uv also shows clear error (future-proofing)."""
        cmd_setup = _project_module.cmd_setup

        # Mock sys.version_info to simulate Python 3.14
        mock_version = MockVersionInfo(3, 14, 1)
        with patch.object(_project_module.sys, "version_info", mock_version):
            # Mock detect_uv to return False (uv not available)
            with patch.object(_project_module, "detect_uv", return_value=False):
                with pytest.raises(SystemExit) as exc_info:
                    cmd_setup([])

                assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "3.14.1" in captured.out
        assert "not yet supported" in captured.out or "not supported" in captured.out

    def test_python_3_12_proceeds(self, mock_project_dir, capsys):
        """Python 3.12 is valid and proceeds past version check."""
        cmd_setup = _project_module.cmd_setup

        # Mock sys.version_info to simulate Python 3.12
        mock_version = MockVersionInfo(3, 12, 4)

        # Mock subprocess and Path to prevent actual venv/pip operations
        mock_run = MagicMock(return_value=MagicMock(returncode=0, stderr=""))
        mock_path_exists = MagicMock(return_value=True)  # Pretend venv exists

        with patch.object(_project_module.sys, "version_info", mock_version):
            with patch.object(_project_module.subprocess, "run", mock_run):
                with patch.object(_project_module.Path, "exists", mock_path_exists):
                    try:
                        cmd_setup([])
                    except (SystemExit, Exception):
                        pass  # May fail for other mocked reasons

        captured = capsys.readouterr()
        # Should NOT show version rejection errors
        assert "too old" not in captured.out
        assert "not yet supported" not in captured.out
        # Should show version was accepted (the checkmark line)
        assert "3.12.4" in captured.out

    def test_python_3_10_proceeds(self, mock_project_dir, capsys):
        """Python 3.10 (minimum) is valid and proceeds past version check."""
        cmd_setup = _project_module.cmd_setup

        # Mock sys.version_info to simulate Python 3.10
        mock_version = MockVersionInfo(3, 10, 12)

        # Mock subprocess and Path to prevent actual venv/pip operations
        mock_run = MagicMock(return_value=MagicMock(returncode=0, stderr=""))
        mock_path_exists = MagicMock(return_value=True)  # Pretend venv exists

        with patch.object(_project_module.sys, "version_info", mock_version):
            with patch.object(_project_module.subprocess, "run", mock_run):
                with patch.object(_project_module.Path, "exists", mock_path_exists):
                    try:
                        cmd_setup([])
                    except (SystemExit, Exception):
                        pass  # May fail for other mocked reasons

        captured = capsys.readouterr()
        # Should NOT show version rejection errors
        assert "too old" not in captured.out
        assert "not yet supported" not in captured.out
        # Should show version was accepted
        assert "3.10.12" in captured.out


class TestTitleCaseProject:
    """Tests for _title_case_project helper."""

    def test_hyphenated_name(self):
        title_case = _project_module._title_case_project
        assert title_case("my-cool-project") == "My Cool Project"

    def test_underscored_name(self):
        title_case = _project_module._title_case_project
        assert title_case("my_cool_project") == "My Cool Project"

    def test_single_word(self):
        title_case = _project_module._title_case_project
        assert title_case("simple") == "Simple"

    def test_mixed_separators(self):
        title_case = _project_module._title_case_project
        assert title_case("a-b_c") == "A B C"

    def test_empty_string(self):
        title_case = _project_module._title_case_project
        assert title_case("") == ""


class TestDeriveRepoUrl:
    """Tests for _derive_repo_url helper."""

    def test_ssh_url(self, tmp_path):
        derive = _project_module._derive_repo_url
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            [
                "git",
                "remote",
                "add",
                "origin",
                "git@github.com:testuser/my-repo.git",
            ],
            cwd=tmp_path,
            capture_output=True,
        )
        assert derive(tmp_path) == "github.com/testuser/my-repo"

    def test_https_url(self, tmp_path):
        derive = _project_module._derive_repo_url
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            [
                "git",
                "remote",
                "add",
                "origin",
                "https://github.com/testuser/my-repo.git",
            ],
            cwd=tmp_path,
            capture_output=True,
        )
        assert derive(tmp_path) == "github.com/testuser/my-repo"

    def test_https_url_without_dot_git(self, tmp_path):
        derive = _project_module._derive_repo_url
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            [
                "git",
                "remote",
                "add",
                "origin",
                "https://github.com/testuser/my-repo",
            ],
            cwd=tmp_path,
            capture_output=True,
        )
        assert derive(tmp_path) == "github.com/testuser/my-repo"

    def test_no_remote(self, tmp_path):
        derive = _project_module._derive_repo_url
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        assert derive(tmp_path) is None

    def test_no_git_repo(self, tmp_path):
        derive = _project_module._derive_repo_url
        assert derive(tmp_path) is None

    def test_unrecognized_url_format_returns_none(self, tmp_path):
        """Unrecognized URL formats (ssh://, git://) return None."""
        derive = _project_module._derive_repo_url
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "remote", "add", "origin", "ssh://git@github.com/owner/repo.git"],
            cwd=tmp_path,
            capture_output=True,
        )
        assert derive(tmp_path) is None


class TestReconfigureExpanded:
    """Tests for expanded reconfigure with 8 new identity patterns."""

    @pytest.fixture
    def mock_project(self, tmp_path):
        """Create a temp project with all files containing upstream patterns."""
        # .serena/project.yml
        serena_dir = tmp_path / ".serena"
        serena_dir.mkdir()
        (serena_dir / "project.yml").write_text("name: my-cool-project\n")

        # .claude/agents/
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "feature-developer-v3.md").write_text(
            'mcp__serena__activate_project("agentive-starter-kit")\n'
        )
        (agents_dir / "planner.md").write_text(
            "# Planner\n\n"
            "#    [X.Y.Z]: https://github.com/movito/"
            "agentive-starter-kit/compare/vPREV...vX.Y.Z\n"
        )

        # pyproject.toml
        (tmp_path / "pyproject.toml").write_text(
            "# Project configuration for Python projects"
            " using the Agentive Starter Kit\n"
            '[build-system]\nrequires = ["setuptools>=61.0"]\n'
        )

        # tests/conftest.py
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "conftest.py").write_text(
            '"""\nShared fixtures for the agentive-starter-kit test suite.\n"""\n'
        )

        # CHANGELOG.md
        (tmp_path / "CHANGELOG.md").write_text(
            "# Changelog\n\n"
            "All notable changes to the Agentive Starter Kit"
            " will be documented in this file.\n\n"
            "## [Unreleased]\n\n"
            "[0.3.2]: https://github.com/movito/"
            "agentive-starter-kit/compare/v0.3.1...v0.3.2\n"
            "[0.3.1]: https://github.com/movito/"
            "agentive-starter-kit/compare/v0.3.0...v0.3.1\n"
        )

        # CLAUDE.md
        (tmp_path / "CLAUDE.md").write_text(
            "# Agentive Starter Kit\n\nSome description.\n"
        )

        # README.md
        (tmp_path / "README.md").write_text("# Agentive Starter Kit\n\nMore content.\n")

        # scripts/logging_config.py
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        (scripts_dir / "logging_config.py").write_text(
            '"""\nLogging Configuration\n\n'
            "Configurable logging infrastructure for the"
            " agentive-starter-kit.\n"
            '"""\n'
        )

        # Initialize git repo with fake remote
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            [
                "git",
                "remote",
                "add",
                "origin",
                "git@github.com:testuser/my-cool-project.git",
            ],
            cwd=tmp_path,
            capture_output=True,
        )

        return tmp_path

    def _run_reconfigure(self, project_dir, **kwargs):
        """Helper to run reconfigure_project."""
        return _project_module.reconfigure_project(project_dir, **kwargs)

    def test_pyproject_comment_replaced(self, mock_project):
        self._run_reconfigure(mock_project)
        content = (mock_project / "pyproject.toml").read_text()
        assert "# Project configuration for my-cool-project" in content
        assert "Agentive Starter Kit" not in content

    def test_conftest_docstring_replaced(self, mock_project):
        self._run_reconfigure(mock_project)
        content = (mock_project / "tests" / "conftest.py").read_text()
        assert "my-cool-project test suite" in content
        assert "agentive-starter-kit test suite" not in content

    def test_changelog_header_replaced(self, mock_project):
        self._run_reconfigure(mock_project)
        content = (mock_project / "CHANGELOG.md").read_text()
        assert "All notable changes to My Cool Project" in content
        assert "Agentive Starter Kit" not in content

    def test_changelog_urls_replaced(self, mock_project):
        self._run_reconfigure(mock_project)
        content = (mock_project / "CHANGELOG.md").read_text()
        assert "github.com/testuser/my-cool-project/compare/" in content
        assert "github.com/movito/agentive-starter-kit" not in content

    def test_claude_md_title_replaced(self, mock_project):
        self._run_reconfigure(mock_project)
        content = (mock_project / "CLAUDE.md").read_text()
        assert "# My Cool Project" in content
        assert "# Agentive Starter Kit" not in content

    def test_readme_title_replaced(self, mock_project):
        self._run_reconfigure(mock_project)
        content = (mock_project / "README.md").read_text()
        assert "# My Cool Project" in content
        assert "# Agentive Starter Kit" not in content

    def test_logging_config_replaced(self, mock_project):
        self._run_reconfigure(mock_project)
        content = (mock_project / "scripts" / "logging_config.py").read_text()
        assert "infrastructure for the my-cool-project" in content
        assert "agentive-starter-kit" not in content

    def test_planner_url_replaced(self, mock_project):
        self._run_reconfigure(mock_project)
        content = (mock_project / ".claude" / "agents" / "planner.md").read_text()
        assert "github.com/testuser/my-cool-project" in content
        assert "github.com/movito/agentive-starter-kit" not in content

    def test_agent_activation_still_works(self, mock_project):
        """Existing Serena activation replacement still works."""
        self._run_reconfigure(mock_project)
        content = (
            mock_project / ".claude" / "agents" / "feature-developer-v3.md"
        ).read_text()
        assert 'activate_project("my-cool-project")' in content

    def test_idempotent(self, mock_project):
        """Running reconfigure twice produces identical results."""
        self._run_reconfigure(mock_project)

        # Snapshot all files after first run
        files_after_first = {}
        for f in mock_project.rglob("*"):
            if f.is_file() and f.suffix in {
                ".md",
                ".toml",
                ".py",
                ".yml",
            }:
                files_after_first[str(f.relative_to(mock_project))] = f.read_text()

        # Run again
        self._run_reconfigure(mock_project)

        # Verify all files unchanged
        for rel_path, first_content in files_after_first.items():
            filepath = mock_project / rel_path
            assert (
                filepath.read_text() == first_content
            ), f"File changed on second run: {rel_path}"

    def test_missing_files_skipped(self, tmp_path, capsys):
        """Gracefully skips files that don't exist."""
        # Minimal project: only .serena/project.yml and .claude/agents
        serena_dir = tmp_path / ".serena"
        serena_dir.mkdir()
        (serena_dir / "project.yml").write_text("name: test-project\n")

        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        # Init git so _derive_repo_url doesn't fail
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)

        self._run_reconfigure(tmp_path)

        captured = capsys.readouterr()
        assert "not found (skipped)" in captured.out

    def test_no_remote_skips_urls(self, tmp_path, capsys):
        """URL replacements skipped when git remote unavailable."""
        serena_dir = tmp_path / ".serena"
        serena_dir.mkdir()
        (serena_dir / "project.yml").write_text("name: test-project\n")

        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        # Create CHANGELOG with upstream URLs
        (tmp_path / "CHANGELOG.md").write_text(
            "[0.3.2]: https://github.com/movito/"
            "agentive-starter-kit/compare/v0.3.1...v0.3.2\n"
        )

        # Init git but NO remote
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)

        self._run_reconfigure(tmp_path)

        # CHANGELOG URLs should NOT be replaced
        content = (tmp_path / "CHANGELOG.md").read_text()
        assert "github.com/movito/agentive-starter-kit" in content

        captured = capsys.readouterr()
        assert "Git remote not available" in captured.out

    def test_summary_output(self, mock_project, capsys):
        """Summary shows updated/skipped counts."""
        self._run_reconfigure(mock_project)
        captured = capsys.readouterr()
        assert "Done:" in captured.out
        assert "updated" in captured.out
        assert "already correct" in captured.out

    def test_verify_flag_runs_audit(self, mock_project, capsys):
        """--verify flag triggers identity leak audit."""
        result = self._run_reconfigure(mock_project, verify=True)
        assert result is True  # No leaks after reconfigure
        captured = capsys.readouterr()
        assert "Verifying" in captured.out
        assert "identity leak" in captured.out.lower()

    def test_verify_returns_false_when_leaks_remain(self, tmp_path):
        """--verify returns False (exit 1) when leaks are detected."""
        serena_dir = tmp_path / ".serena"
        serena_dir.mkdir()
        (serena_dir / "project.yml").write_text("name: test-project\n")

        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        # Create a file with a leak that reconfigure won't fix
        # (not in the replacement list)
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "other.py").write_text(
            "# references agentive-starter-kit somewhere\n"
        )

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)

        result = self._run_reconfigure(tmp_path, verify=True)
        assert result is False

    def test_returns_false_when_file_errors(self, tmp_path, capsys):
        """reconfigure_project returns False when file operations error."""
        serena_dir = tmp_path / ".serena"
        serena_dir.mkdir()
        (serena_dir / "project.yml").write_text("name: test-project\n")

        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        # Create pyproject.toml as a directory to trigger an error
        (tmp_path / "pyproject.toml").mkdir()

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)

        result = self._run_reconfigure(tmp_path)
        assert result is False
        captured = capsys.readouterr()
        assert "error" in captured.out.lower()


class TestVerifyIdentityLeaks:
    """Tests for _verify_identity_leaks function."""

    def test_clean_project_reports_zero(self, tmp_path, capsys):
        """No leaks when project has been reconfigured."""
        # Create a file with no upstream references
        (tmp_path / "README.md").write_text("# My Project\n")
        verify = _project_module._verify_identity_leaks
        count = verify(tmp_path)
        assert count == 0
        captured = capsys.readouterr()
        assert "No identity leaks found" in captured.out

    def test_detects_remaining_leaks(self, tmp_path, capsys):
        """Reports files that still contain upstream references."""
        (tmp_path / "leaked.py").write_text("# This references agentive-starter-kit\n")
        verify = _project_module._verify_identity_leaks
        count = verify(tmp_path)
        assert count == 1
        captured = capsys.readouterr()
        assert "remaining identity leak" in captured.out.lower()

    def test_excludes_legitimate_references(self, tmp_path):
        """Legitimate reference locations are excluded from scan."""
        # Create excluded directories with upstream references
        adversarial_dir = tmp_path / ".adversarial"
        adversarial_dir.mkdir()
        (adversarial_dir / "config.md").write_text("agentive-starter-kit reference\n")

        agent_ctx = tmp_path / ".agent-context"
        agent_ctx.mkdir()
        (agent_ctx / "handoff.md").write_text("agentive-starter-kit reference\n")

        decisions_dir = tmp_path / "docs" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "adr.md").write_text("agentive-starter-kit reference\n")

        tasks_dir = tmp_path / "delegation" / "tasks"
        tasks_dir.mkdir(parents=True)
        (tasks_dir / "ASK-0036.md").write_text("agentive-starter-kit reference\n")

        # onboarding.md at any location
        (tmp_path / "onboarding.md").write_text("agentive-starter-kit reference\n")

        # tests/ directory (test fixtures contain upstream strings)
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_project_script.py").write_text(
            "agentive-starter-kit reference in fixture\n"
        )

        verify = _project_module._verify_identity_leaks
        count = verify(tmp_path)
        assert count == 0

    def test_exclusion_uses_path_segments_not_substrings(self, tmp_path):
        """Exclusion matches path segments, not substrings of filenames."""
        # A file with "tests" in its name (not in a tests/ directory)
        # should NOT be excluded
        (tmp_path / "my_tests_helper.py").write_text("agentive-starter-kit reference\n")
        verify = _project_module._verify_identity_leaks
        count = verify(tmp_path)
        assert count == 1
