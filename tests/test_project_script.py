"""
Tests for scripts/core/project CLI commands.

Focus: install-evaluators command with mocked subprocess calls.
"""

import importlib.util
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from conftest import MockVersionInfo


@pytest.fixture(autouse=True)
def _isolate_git_env(monkeypatch):
    """Strip ambient GIT_* so tmp-repo git calls can't escape to the real repo.

    pre-commit exports GIT_DIR / GIT_INDEX_FILE during hooks — and in a git
    WORKTREE the exported GIT_DIR is absolute, so every `git` subprocess in
    this module (TestDeriveRepoUrl, TestReconfigureExpanded, ...) resolved
    the REAL repo instead of its tmp_path fixture, failing the pytest-fast
    hook on any worktree commit. Same isolation as
    test_preflight_check._clean_env — the GIT_DIR gotcha in
    .kit/context/workflows/TESTING-WORKFLOW.md. Surfaced by the KIT-0043
    worktree pilot.
    """
    for key in list(os.environ):
        if key.startswith("GIT_"):
            monkeypatch.delenv(key, raising=False)


# Load the project script as a module
_script_path = Path(__file__).parent.parent / "scripts" / "core" / "project"
_spec = importlib.util.spec_from_loader("project_script", loader=None)
_project_module = importlib.util.module_from_spec(_spec)

# Read and execute the script to get the functions
# Inject __file__ so Path(__file__) works in cmd_setup
with open(_script_path, encoding="utf-8") as f:
    _project_module.__dict__["__file__"] = str(_script_path)
    exec(f.read(), _project_module.__dict__)


class TestInstallEvaluatorsCommand:
    """Tests for install-evaluators command."""

    @pytest.fixture(autouse=True)
    def _no_cli_ensure(self):
        """Stub the CLI-ensure step for the LIBRARY-install tests.

        These tests drive subprocess.run with positional side_effect
        lists ([git --version, git clone]), so any additional subprocess
        call would shift the list and fail them for the wrong reason.
        The CLI step (KIT-0083) is covered on its own in
        TestEnsureAdversarialCli; isolating it here keeps these tests
        about the library install.

        Autouse rather than per-test: without it these tests pass or
        fail depending on whether the MACHINE happens to have
        `adversarial` on PATH (the real shutil.which short-circuits the
        step) — exactly the environment-dependence that let issue #103
        ship unnoticed.
        """
        with patch.object(_project_module, "_ensure_adversarial_cli"):
            yield

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
        version_file.write_text("v0.2.2 (abc12345)\n", encoding="utf-8")

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
        version_file.write_text("v0.2.2 (abc12345)\n", encoding="utf-8")

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

    def test_python_3_13_proceeds(self, mock_project_dir, capsys):
        """Python 3.13 is valid — the historical <3.13 ceiling is gone (KIT-0065)."""
        cmd_setup = _project_module.cmd_setup

        # Mock sys.version_info to simulate Python 3.13
        mock_version = MockVersionInfo(3, 13, 0)

        # Mock subprocess and Path to prevent actual venv/pip operations
        mock_run = MagicMock(return_value=MagicMock(returncode=0, stderr=""))
        mock_path_exists = MagicMock(return_value=True)  # Pretend venv exists

        with patch.object(_project_module.sys, "version_info", mock_version):
            with patch.object(_project_module.subprocess, "run", mock_run):
                with patch.object(_project_module.Path, "exists", mock_path_exists):
                    # is_symlink False: the KIT-0071 symlink guard reads
                    # the REAL .venv otherwise (a pre-KIT-0071 worktree
                    # would trip it) — this test is about versions only
                    with patch.object(
                        _project_module.Path,
                        "is_symlink",
                        MagicMock(return_value=False),
                    ):
                        cmd_setup([])  # must complete without raising

        captured = capsys.readouterr()
        # Should NOT show version rejection errors
        assert "too old" not in captured.out
        assert "not yet supported" not in captured.out
        # Should show version was accepted (the checkmark line)
        assert "3.13.0" in captured.out

    def test_python_3_14_proceeds(self, mock_project_dir, capsys):
        """Python 3.14 is valid and proceeds past version check."""
        cmd_setup = _project_module.cmd_setup

        # Mock sys.version_info to simulate Python 3.14
        mock_version = MockVersionInfo(3, 14, 1)

        # Mock subprocess and Path to prevent actual venv/pip operations
        mock_run = MagicMock(return_value=MagicMock(returncode=0, stderr=""))
        mock_path_exists = MagicMock(return_value=True)  # Pretend venv exists

        with patch.object(_project_module.sys, "version_info", mock_version):
            with patch.object(_project_module.subprocess, "run", mock_run):
                with patch.object(_project_module.Path, "exists", mock_path_exists):
                    # is_symlink False: the KIT-0071 symlink guard reads
                    # the REAL .venv otherwise (a pre-KIT-0071 worktree
                    # would trip it) — this test is about versions only
                    with patch.object(
                        _project_module.Path,
                        "is_symlink",
                        MagicMock(return_value=False),
                    ):
                        cmd_setup([])  # must complete without raising

        captured = capsys.readouterr()
        # Should NOT show version rejection errors
        assert "too old" not in captured.out
        assert "not yet supported" not in captured.out
        # Should show version was accepted
        assert "3.14.1" in captured.out

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
                    # is_symlink False: the KIT-0071 symlink guard reads
                    # the REAL .venv otherwise (a pre-KIT-0071 worktree
                    # would trip it) — this test is about versions only
                    with patch.object(
                        _project_module.Path,
                        "is_symlink",
                        MagicMock(return_value=False),
                    ):
                        cmd_setup([])  # must complete without raising

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
                    # is_symlink False: the KIT-0071 symlink guard reads
                    # the REAL .venv otherwise (a pre-KIT-0071 worktree
                    # would trip it) — this test is about versions only
                    with patch.object(
                        _project_module.Path,
                        "is_symlink",
                        MagicMock(return_value=False),
                    ):
                        cmd_setup([])  # must complete without raising

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


REPO_ROOT = Path(__file__).resolve().parent.parent

# Every file the mock_project fixture models, keyed by its REAL relative
# path in the repo. test_fixture_paths_exist_in_real_tree pins each key
# to the actual tree: a fixture modeling a nonexistent layout masked the
# A02 regression (reconfigure silently skipping the moved
# scripts/core/logging_config.py) for months (KIT-0068).
MOCK_PROJECT_FILES = {
    ".serena/project.yml": "name: my-cool-project\n",
    ".claude/agents/feature-developer.md": (
        'mcp__serena__activate_project("agentive-starter-kit")\n'
    ),
    ".claude/agents/planner.md": (
        "# Planner\n\n"
        "#    [X.Y.Z]: https://github.com/movito/"
        "agentive-starter-kit/compare/vPREV...vX.Y.Z\n"
    ),
    "pyproject.toml": (
        "# Project configuration for Python projects"
        " using the Agentive Starter Kit\n"
        '[build-system]\nrequires = ["setuptools>=61.0"]\n'
    ),
    "tests/conftest.py": (
        '"""\nShared fixtures for the agentive-starter-kit test suite.\n"""\n'
    ),
    "CHANGELOG.md": (
        "# Changelog\n\n"
        "All notable changes to the Agentive Starter Kit"
        " will be documented in this file.\n\n"
        "## [Unreleased]\n\n"
        "[0.3.2]: https://github.com/movito/"
        "agentive-starter-kit/compare/v0.3.1...v0.3.2\n"
        "[0.3.1]: https://github.com/movito/"
        "agentive-starter-kit/compare/v0.3.0...v0.3.1\n"
    ),
    "CLAUDE.md": "# Agentive Starter Kit\n\nSome description.\n",
    "README.md": "# Agentive Starter Kit\n\nMore content.\n",
    "scripts/core/logging_config.py": (
        '"""\nLogging Configuration\n\n'
        "Configurable logging infrastructure for the"
        " agentive-starter-kit.\n"
        '"""\n'
    ),
}

# Modeled paths that are runtime-generated in a real checkout (never
# tracked); each maps to the tracked witness proving the path is still
# the current layout.
MOCK_GENERATED_WITNESSES = {
    ".serena/project.yml": ".serena/project.yml.template",
}


class TestReconfigureExpanded:
    """Tests for expanded reconfigure with 8 new identity patterns."""

    @pytest.fixture
    def mock_project(self, tmp_path):
        """Create a temp project with all files containing upstream patterns."""
        for rel_path, content in MOCK_PROJECT_FILES.items():
            target = tmp_path / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

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
        content = (mock_project / "pyproject.toml").read_text(encoding="utf-8")
        assert "# Project configuration for my-cool-project" in content
        assert "Agentive Starter Kit" not in content

    def test_conftest_docstring_replaced(self, mock_project):
        self._run_reconfigure(mock_project)
        content = (mock_project / "tests" / "conftest.py").read_text(encoding="utf-8")
        assert "my-cool-project test suite" in content
        assert "agentive-starter-kit test suite" not in content

    def test_changelog_header_replaced(self, mock_project):
        self._run_reconfigure(mock_project)
        content = (mock_project / "CHANGELOG.md").read_text(encoding="utf-8")
        assert "All notable changes to My Cool Project" in content
        assert "Agentive Starter Kit" not in content

    def test_changelog_urls_replaced(self, mock_project):
        self._run_reconfigure(mock_project)
        content = (mock_project / "CHANGELOG.md").read_text(encoding="utf-8")
        assert "github.com/testuser/my-cool-project/compare/" in content
        assert "github.com/movito/agentive-starter-kit" not in content

    def test_claude_md_title_replaced(self, mock_project):
        self._run_reconfigure(mock_project)
        content = (mock_project / "CLAUDE.md").read_text(encoding="utf-8")
        assert "# My Cool Project" in content
        assert "# Agentive Starter Kit" not in content

    def test_readme_title_replaced(self, mock_project):
        self._run_reconfigure(mock_project)
        content = (mock_project / "README.md").read_text(encoding="utf-8")
        assert "# My Cool Project" in content
        assert "# Agentive Starter Kit" not in content

    def test_logging_config_replaced(self, mock_project):
        self._run_reconfigure(mock_project)
        content = (mock_project / "scripts" / "core" / "logging_config.py").read_text(
            encoding="utf-8"
        )
        assert "infrastructure for the my-cool-project" in content
        assert "agentive-starter-kit" not in content

    def test_planner_url_replaced(self, mock_project):
        self._run_reconfigure(mock_project)
        content = (mock_project / ".claude" / "agents" / "planner.md").read_text(
            encoding="utf-8"
        )
        assert "github.com/testuser/my-cool-project" in content
        assert "github.com/movito/agentive-starter-kit" not in content

    def test_agent_activation_still_works(self, mock_project):
        """Existing Serena activation replacement still works."""
        self._run_reconfigure(mock_project)
        content = (
            mock_project / ".claude" / "agents" / "feature-developer.md"
        ).read_text(encoding="utf-8")
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
                files_after_first[str(f.relative_to(mock_project))] = f.read_text(
                    encoding="utf-8"
                )

        # Run again
        self._run_reconfigure(mock_project)

        # Verify all files unchanged
        for rel_path, first_content in files_after_first.items():
            filepath = mock_project / rel_path
            assert (
                filepath.read_text(encoding="utf-8") == first_content
            ), f"File changed on second run: {rel_path}"

    def test_missing_files_skipped(self, tmp_path, capsys):
        """Gracefully skips files that don't exist."""
        # Minimal project: only .serena/project.yml and .claude/agents
        serena_dir = tmp_path / ".serena"
        serena_dir.mkdir()
        (serena_dir / "project.yml").write_text(
            "name: test-project\n", encoding="utf-8"
        )

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
        (serena_dir / "project.yml").write_text(
            "name: test-project\n", encoding="utf-8"
        )

        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        # Create CHANGELOG with upstream URLs
        (tmp_path / "CHANGELOG.md").write_text(
            "[0.3.2]: https://github.com/movito/"
            "agentive-starter-kit/compare/v0.3.1...v0.3.2\n",
            encoding="utf-8",
        )

        # Init git but NO remote
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)

        self._run_reconfigure(tmp_path)

        # CHANGELOG URLs should NOT be replaced
        content = (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8")
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
        (serena_dir / "project.yml").write_text(
            "name: test-project\n", encoding="utf-8"
        )

        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        # Create a file with a leak that reconfigure won't fix
        # (not in the replacement list)
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "other.py").write_text(
            "# references agentive-starter-kit somewhere\n", encoding="utf-8"
        )

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)

        result = self._run_reconfigure(tmp_path, verify=True)
        assert result is False

    def test_returns_false_when_file_errors(self, tmp_path, capsys):
        """reconfigure_project returns False when file operations error."""
        serena_dir = tmp_path / ".serena"
        serena_dir.mkdir()
        (serena_dir / "project.yml").write_text(
            "name: test-project\n", encoding="utf-8"
        )

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
        (tmp_path / "README.md").write_text("# My Project\n", encoding="utf-8")
        verify = _project_module._verify_identity_leaks
        count = verify(tmp_path)
        assert count == 0
        captured = capsys.readouterr()
        assert "No identity leaks found" in captured.out

    def test_detects_remaining_leaks(self, tmp_path, capsys):
        """Reports files that still contain upstream references."""
        (tmp_path / "leaked.py").write_text(
            "# This references agentive-starter-kit\n", encoding="utf-8"
        )
        verify = _project_module._verify_identity_leaks
        count = verify(tmp_path)
        assert count == 1
        captured = capsys.readouterr()
        assert "remaining identity leak" in captured.out.lower()

    def test_excludes_legitimate_references(self, tmp_path):
        """Legitimate reference locations are excluded from scan."""
        # Create excluded directories with upstream references
        adversarial_dir = tmp_path / ".adversarial"
        adversarial_dir.mkdir(parents=True)
        (adversarial_dir / "config.md").write_text(
            "agentive-starter-kit reference\n", encoding="utf-8"
        )

        agent_ctx = tmp_path / ".kit" / "context"
        agent_ctx.mkdir(parents=True)
        (agent_ctx / "handoff.md").write_text(
            "agentive-starter-kit reference\n", encoding="utf-8"
        )

        adr_dir = tmp_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "about-adr.md").write_text(
            "agentive-starter-kit reference\n", encoding="utf-8"
        )

        tasks_dir = tmp_path / ".kit" / "tasks"
        tasks_dir.mkdir(parents=True)
        (tasks_dir / "ASK-0036.md").write_text(
            "agentive-starter-kit reference\n", encoding="utf-8"
        )

        # onboarding.md at any location
        (tmp_path / "onboarding.md").write_text(
            "agentive-starter-kit reference\n", encoding="utf-8"
        )

        # tests/ directory (test fixtures contain upstream strings)
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_project_script.py").write_text(
            "agentive-starter-kit reference in fixture\n", encoding="utf-8"
        )

        verify = _project_module._verify_identity_leaks
        count = verify(tmp_path)
        assert count == 0

    def test_exclusion_uses_path_segments_not_substrings(self, tmp_path):
        """Exclusion matches path segments, not substrings of filenames."""
        # A file with "tests" in its name (not in a tests/ directory)
        # should NOT be excluded
        (tmp_path / "my_tests_helper.py").write_text(
            "agentive-starter-kit reference\n", encoding="utf-8"
        )
        verify = _project_module._verify_identity_leaks
        count = verify(tmp_path)
        assert count == 1

    def test_excludes_upstream_prefix_files(self, tmp_path):
        """docs/UPSTREAM prefix matches files like UPSTREAM-CHANGES-*.md."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "UPSTREAM-CHANGES-2025-01-28.md").write_text(
            "agentive-starter-kit reference\n", encoding="utf-8"
        )
        verify = _project_module._verify_identity_leaks
        count = verify(tmp_path)
        assert count == 0


# TestMoveTaskMetadataSync migrated to tests/agentive_kit/test_lifecycle.py
# (KIT-0090 F3): move_task and the coordination-metadata sync now live in
# the agentive-kit package, including the KIT-0086 single-writer guard.


class TestLifecycleDelegation:
    """KIT-0090 PR 1: the script's lifecycle commands delegate to the
    agentive-kit package — the dispatch itself needs subprocess-level
    coverage (evaluator finding, PR 1 trio)."""

    def _run(self, tree, *args):
        return subprocess.run(
            [sys.executable, str(tree / "scripts" / "core" / "project"), *args],
            capture_output=True,
            text=True,
            timeout=60,
        )

    @pytest.fixture
    def kit_tree_with_package(self, tmp_path):
        """A project tree carrying the script AND the package source —
        the dogfood path (_kit_lifecycle's in-repo fallback)."""
        pkg_src = Path(__file__).parent.parent / "packages" / "agentive-kit" / "src"
        if not pkg_src.is_dir():
            # Skip decided BEFORE any tree building (CodeRabbit, PR #108)
            pytest.skip("agentive-kit package source present only in the kit repo")
        core = tmp_path / "scripts" / "core"
        core.mkdir(parents=True)
        shutil.copy(_script_path, core / "project")
        shutil.copytree(pkg_src, tmp_path / "packages" / "agentive-kit" / "src")
        tasks = tmp_path / ".kit" / "tasks"
        for folder in ("2-todo", "3-in-progress"):
            (tasks / folder).mkdir(parents=True)
        (tasks / "2-todo" / "KIT-1234-sample.md").write_text(
            "**Status**: Todo\n", encoding="utf-8"
        )
        return tmp_path

    def test_start_delegates_and_moves(self, kit_tree_with_package):
        tree = kit_tree_with_package
        result = self._run(tree, "start", "KIT-1234")
        assert result.returncode == 0, result.stdout + result.stderr
        moved = tree / ".kit" / "tasks" / "3-in-progress" / "KIT-1234-sample.md"
        assert moved.exists()
        assert "In Progress" in result.stdout

    def test_validate_delegates(self, kit_tree_with_package):
        result = self._run(kit_tree_with_package, "validate")
        assert result.returncode == 0, result.stdout + result.stderr
        assert "matching Status and folder" in result.stdout

    def test_missing_package_fails_loud_with_install_command(self, tmp_path):
        # A consumer that synced the delegating script before phase 3
        # (no installed CLI, no packages/ tree) must get the exact
        # install instruction, never a traceback.
        #
        # Guard (CodeRabbit, PR #108): once agentive-kit is pip-
        # installed into this interpreter (the PR-4 dogfood switch),
        # the script's FIRST import branch succeeds and this test's
        # premise is gone — probe the subprocess view and skip then.
        probe = subprocess.run(
            [sys.executable, "-c", "import agentive_kit"],
            capture_output=True,
            timeout=60,
            cwd=tmp_path,
        )
        if probe.returncode == 0:
            pytest.skip("agentive-kit is installed in this interpreter")
        core = tmp_path / "scripts" / "core"
        core.mkdir(parents=True)
        shutil.copy(_script_path, core / "project")
        (tmp_path / ".kit" / "tasks" / "2-todo").mkdir(parents=True)
        result = subprocess.run(
            [sys.executable, str(core / "project"), "validate"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=tmp_path,
        )
        assert result.returncode == 1
        assert "uv tool install agentive-kit" in result.stdout
        assert "Traceback" not in result.stderr


class TestFixtureHonesty:
    """The A02 guard (KIT-0068): every path a fixture models must exist
    in the real repo tree. A fixture built on the pre-v0.4.0 layout
    (scripts/logging_config.py) kept test_logging_config_replaced green
    while the real command silently skipped the moved file for months."""

    _kit_only = pytest.mark.skipif(
        not (REPO_ROOT / "scripts" / "local" / "bootstrap").exists(),
        reason="kit source tree only (consumer checkouts ship a subset)",
    )

    @_kit_only
    @pytest.mark.parametrize("rel_path", sorted(MOCK_PROJECT_FILES))
    def test_fixture_paths_exist_in_real_tree(self, rel_path):
        if rel_path in MOCK_GENERATED_WITNESSES:
            witness = MOCK_GENERATED_WITNESSES[rel_path]
            assert (REPO_ROOT / witness).exists(), (
                f"fixture models generated file {rel_path}, but its tracked"
                f" witness {witness} is gone — layout moved, update the fixture"
            )
        else:
            assert (REPO_ROOT / rel_path).exists(), (
                f"fixture models {rel_path}, which does not exist in the real"
                f" repo — the fixture is lying about the layout (A02 class)"
            )


class TestCallerPathsRealTree:
    """Regression pins for KIT-0068 A00/A01: the module-level caller
    paths in scripts/core/project must point at files that exist."""

    def test_linearsync_script_exists(self):
        assert (REPO_ROOT / _project_module.LINEARSYNC_SCRIPT).exists()

    def test_create_agent_script_exists(self):
        assert (REPO_ROOT / _project_module.CREATE_AGENT_SCRIPT).exists()

    @pytest.fixture
    def bare_tree(self, tmp_path):
        """A project tree carrying the CLI but no scripts/optional/ —
        the consumer case the friendly errors exist for."""
        core = tmp_path / "scripts" / "core"
        core.mkdir(parents=True)
        shutil.copy(_script_path, core / "project")
        return tmp_path

    def _run(self, tree, *args):
        return subprocess.run(
            [sys.executable, str(tree / "scripts" / "core" / "project"), *args],
            capture_output=True,
            text=True,
            timeout=60,
        )

    def test_linearsync_missing_layer_names_the_file(self, bare_tree):
        result = self._run(bare_tree, "linearsync")
        assert result.returncode == 1
        assert "scripts/optional/sync_tasks_to_linear.py not found" in result.stdout

    def test_create_agent_missing_layer_names_the_file(self, bare_tree):
        result = self._run(bare_tree, "create-agent")
        assert result.returncode == 1
        assert "scripts/optional/create-agent.sh not found" in result.stdout

    def test_version_reads_core_version_file(self, bare_tree):
        (bare_tree / "scripts" / "core" / "VERSION").write_text(
            "9.9.9\n", encoding="utf-8"
        )
        result = self._run(bare_tree, "version")
        assert result.returncode == 0
        assert "v9.9.9" in result.stdout

    def test_version_matches_real_version_file(self):
        """AC pin: `project version` output matches scripts/core/VERSION."""
        real_version = (
            (REPO_ROOT / "scripts" / "core" / "VERSION")
            .read_text(encoding="utf-8")
            .strip()
        )
        result = subprocess.run(
            [sys.executable, str(_script_path), "version"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
        assert f"v{real_version}" in result.stdout

    def test_version_missing_file_fails_loud(self, bare_tree):
        result = self._run(bare_tree, "version")
        assert result.returncode == 1
        assert "VERSION" in result.stdout


class TestRefBypassesPinRead:
    """--ref must not require a readable pyproject pin (o3 review,
    KIT-0068): planning-shape repos have no pyproject.toml, and the
    pin reader's own error message tells users to pass --ref."""

    @pytest.fixture(autouse=True)
    def _no_cli_ensure(self):
        """See TestInstallEvaluatorsCommand._no_cli_ensure (KIT-0083)."""
        with patch.object(_project_module, "_ensure_adversarial_cli"):
            yield

    def test_ref_skips_pin_reader(self, tmp_path, capsys):
        evaluators_dir = tmp_path / ".adversarial" / "evaluators"
        evaluators_dir.mkdir(parents=True)

        with patch.object(
            _project_module,
            "_get_evaluator_library_version",
            side_effect=AssertionError("pin reader must not run with --ref"),
        ):
            with patch.object(_project_module, "subprocess") as mock_subprocess:
                mock_subprocess.TimeoutExpired = subprocess.TimeoutExpired
                mock_subprocess.run.side_effect = [
                    MagicMock(returncode=0),  # git --version
                    MagicMock(returncode=1, stderr="not found"),  # clone fails
                ]
                with pytest.raises(SystemExit):
                    _project_module.cmd_install_evaluators(
                        ["--ref", "v9.9.9"], tmp_path
                    )

        assert "v9.9.9" in capsys.readouterr().out


class TestNoOpRerunWithoutPin:
    """A no-op rerun (already installed, no --force) must succeed on a
    repo with no readable pyproject pin — the pin is only needed to
    clone (BugBot round 2, KIT-0068)."""

    @pytest.fixture(autouse=True)
    def _no_cli_ensure(self):
        """See TestInstallEvaluatorsCommand._no_cli_ensure (KIT-0083).

        The CLI step on THIS path (already-installed rerun) is asserted
        separately by TestInstallEvaluatorsEnsuresCli — the #103 shape
        is 'library present, CLI absent', so it must not be lost here.
        """
        with patch.object(_project_module, "_ensure_adversarial_cli"):
            yield

    def test_already_installed_skips_pin_read(self, tmp_path, capsys):
        evaluators_dir = tmp_path / ".adversarial" / "evaluators"
        evaluators_dir.mkdir(parents=True)
        (evaluators_dir / ".installed-version").write_text(
            "v0.9.0 (abc12345)\n", encoding="utf-8"
        )

        with patch.object(
            _project_module,
            "_get_evaluator_library_version",
            side_effect=AssertionError("pin reader must not run on no-op rerun"),
        ):
            with patch.object(_project_module, "subprocess") as mock_subprocess:
                mock_subprocess.TimeoutExpired = subprocess.TimeoutExpired
                mock_subprocess.run.return_value = MagicMock(returncode=0)
                _project_module.cmd_install_evaluators([], tmp_path)

        assert "already installed" in capsys.readouterr().out


class TestSetupVenvSymlinkGuard:
    """KIT-0071 (KIT-0065 incident): `project setup` must refuse to
    operate through a symlinked .venv — a rebuild through the link
    mutates the TARGET venv (KIT-0065 emptied the primary clone's).

    Runs the REAL script copied into a tmp tree (cmd_setup derives the
    project dir from __file__, so the copy anchors it at the fixture)."""

    @staticmethod
    def _fake_tree(tmp_path):
        script_src = Path(__file__).parent.parent / "scripts" / "core" / "project"
        core = tmp_path / "scripts" / "core"
        core.mkdir(parents=True)
        shutil.copy(script_src, core / "project")
        return core / "project"

    def _run_setup(self, script, *args):
        return subprocess.run(
            [sys.executable, str(script), "setup", *args],
            capture_output=True,
            text=True,
            timeout=60,
        )

    def test_symlinked_venv_refused(self, tmp_path):
        script = self._fake_tree(tmp_path)
        target = tmp_path / "target-venv"
        (target / "bin").mkdir(parents=True)
        sentinel = target / "bin" / "python"
        sentinel.write_text("#!/bin/sh\n", encoding="utf-8")
        (tmp_path / ".venv").symlink_to(target)

        result = self._run_setup(script)
        assert result.returncode == 1
        assert "SYMLINK" in result.stdout
        assert "KIT-0065" in result.stdout
        # the guard fired before anything touched the target venv
        assert sentinel.exists()
        assert (tmp_path / ".venv").is_symlink()

    def test_symlinked_venv_refused_even_with_force(self, tmp_path):
        script = self._fake_tree(tmp_path)
        target = tmp_path / "target-venv"
        target.mkdir()
        (tmp_path / ".venv").symlink_to(target)

        result = self._run_setup(script, "--force")
        assert result.returncode == 1
        assert "SYMLINK" in result.stdout
        assert target.exists()

    def test_dangling_venv_symlink_refused(self, tmp_path):
        # exists() is False for a dangling link — the guard must still fire
        script = self._fake_tree(tmp_path)
        (tmp_path / ".venv").symlink_to(tmp_path / "gone")

        result = self._run_setup(script)
        assert result.returncode == 1
        assert "SYMLINK" in result.stdout

    def test_no_hooks_flag_skips_hook_install(self, tmp_path):
        """--no-hooks (worktree provisioning): hooks live in the SHARED
        common git dir; a worktree setup must not re-point them."""
        script = self._fake_tree(tmp_path)
        venv_bin = tmp_path / ".venv" / "bin"
        venv_bin.mkdir(parents=True)
        (venv_bin / "python").write_text("#!/bin/sh\n", encoding="utf-8")
        for stub in ("pip", "pre-commit"):
            stub_path = venv_bin / stub
            stub_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            stub_path.chmod(0o755)

        result = self._run_setup(script, "--no-hooks")
        assert result.returncode == 0, result.stdout + result.stderr
        assert "Skipping pre-commit hook install" in result.stdout
        assert "Pre-commit hooks installed" not in result.stdout

    def test_refusal_in_worktree_recommends_no_hooks(self, tmp_path):
        """BugBot (this PR): in a linked worktree (.git is a FILE) the
        refusal's rerun advice must carry --no-hooks."""
        script = self._fake_tree(tmp_path)
        (tmp_path / ".git").write_text(
            "gitdir: /somewhere/.git/worktrees/x\n", encoding="utf-8"
        )
        target = tmp_path / "target-venv"
        target.mkdir()
        (tmp_path / ".venv").symlink_to(target)

        result = self._run_setup(script)
        assert result.returncode == 1
        assert "setup --no-hooks" in result.stdout

    def test_refusal_outside_worktree_plain_setup(self, tmp_path):
        """In a normal clone (.git is a dir or absent) the advice stays
        plain setup — hooks belong here."""
        script = self._fake_tree(tmp_path)
        (tmp_path / ".git").mkdir()
        target = tmp_path / "target-venv"
        target.mkdir()
        (tmp_path / ".venv").symlink_to(target)

        result = self._run_setup(script)
        assert result.returncode == 1
        assert "--no-hooks" not in result.stdout


class TestReconfigureMissingConfigRemedy:
    """displayed_commands_are_contracts (KIT-0067): the remedy printed
    when .serena/project.yml is missing must be a complete, parseable
    shell command — pinned against the ACTUAL printed output."""

    @pytest.mark.parametrize("dirname", ["plain", "dir with spaces"])
    def test_missing_serena_config_remedy_is_valid_shell(
        self, tmp_path, capsys, dirname
    ):
        import re as _re

        project_dir = tmp_path / dirname
        project_dir.mkdir()
        assert _project_module.reconfigure_project(project_dir) is False
        out = capsys.readouterr().out
        match = _re.search(r"Run: (.+?)  #", out)
        assert match, f"remedy line missing from output:\n{out}"
        proc = subprocess.run(
            ["bash", "-n", "-c", match.group(1)],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, proc.stderr
        # pin the actual remedy, not just any parseable shell
        # (CodeRabbit, PR #98): cd into the named project dir, then the
        # real setup script
        assert match.group(1).startswith("cd ")
        assert match.group(1).endswith("&& bash .serena/setup-serena.sh")
        # root-scoped: the command names the project dir, not a cwd guess
        assert dirname in match.group(1)


class TestEnsureAdversarialCli:
    """KIT-0083 / issue #103: install-evaluators must ensure the CLI too.

    All installs are stubbed — these tests never touch the network and
    never run a real `uv tool install`.
    """

    @pytest.fixture
    def project_with_pin(self, tmp_path):
        """A project whose .adversarial/config.yml carries the CLI pin."""
        adv = tmp_path / ".adversarial"
        adv.mkdir()
        (adv / "config.yml").write_text(
            'task_directory: .kit/tasks/\nadversarial_cli_version: "1.0.1"\n',
            encoding="utf-8",
        )
        return tmp_path

    def test_present_working_cli_is_not_reinstalled(self, project_with_pin, capsys):
        """A WORKING CLI short-circuits: no install attempt at all.

        Keys on _adversarial_cli_works, not shutil.which — presence alone
        is no longer the gate (a present-but-broken binary must still
        trigger a reinstall; see TestAdversarialCliLiveness).
        """
        with patch.object(_project_module, "_adversarial_cli_works", return_value=True):
            with patch.object(_project_module, "subprocess") as mock_sub:
                _project_module._ensure_adversarial_cli(project_with_pin)
                mock_sub.run.assert_not_called()
        assert "already installed" in capsys.readouterr().out

    def test_missing_cli_installs_at_the_pinned_version(self, project_with_pin, capsys):
        """Absent CLI + uv present → uv tool install at the config.yml pin."""
        which = {"adversarial": None, "uv": "/usr/bin/uv"}
        calls = []

        def fake_which(name):
            return which.get(name)

        with patch.object(_project_module.shutil, "which", side_effect=fake_which):
            with patch.object(_project_module, "subprocess") as mock_sub:
                mock_sub.TimeoutExpired = subprocess.TimeoutExpired
                mock_sub.run.side_effect = lambda *a, **k: (
                    calls.append(a[0]) or MagicMock(returncode=0, stderr="")
                )
                _project_module._ensure_adversarial_cli(project_with_pin)

        assert calls == [["uv", "tool", "install", "adversarial-workflow==1.0.1"]]

    def test_uv_absent_prints_command_and_continues(self, project_with_pin, capsys):
        """No uv → instruct, never raise: the library install is the
        primary job and must not fail over the optional CLI step."""
        with patch.object(_project_module.shutil, "which", return_value=None):
            with patch.object(_project_module, "subprocess") as mock_sub:
                _project_module._ensure_adversarial_cli(project_with_pin)
                mock_sub.run.assert_not_called()
        out = capsys.readouterr().out
        assert "uv tool install adversarial-workflow==1.0.1" in out
        assert "uv is not installed" in out

    def test_install_failure_does_not_raise(self, project_with_pin, capsys):
        """A failed install degrades to advice — never a SystemExit."""
        which = {"adversarial": None, "uv": "/usr/bin/uv"}
        with patch.object(
            _project_module.shutil, "which", side_effect=lambda n: which.get(n)
        ):
            with patch.object(_project_module, "subprocess") as mock_sub:
                mock_sub.TimeoutExpired = subprocess.TimeoutExpired
                mock_sub.run.return_value = MagicMock(returncode=1, stderr="boom")
                _project_module._ensure_adversarial_cli(project_with_pin)
        assert "Retry manually" in capsys.readouterr().out

    def test_install_timeout_does_not_raise(self, project_with_pin, capsys):
        which = {"adversarial": None, "uv": "/usr/bin/uv"}
        with patch.object(
            _project_module.shutil, "which", side_effect=lambda n: which.get(n)
        ):
            with patch.object(_project_module, "subprocess") as mock_sub:
                mock_sub.TimeoutExpired = subprocess.TimeoutExpired
                mock_sub.run.side_effect = subprocess.TimeoutExpired(
                    cmd="uv tool install", timeout=300
                )
                _project_module._ensure_adversarial_cli(project_with_pin)
        assert "timed out" in capsys.readouterr().out

    def test_install_succeeds_but_not_on_path_warns(self, project_with_pin, capsys):
        """uv installs into ~/.local/bin: a 'successful' install whose
        binary stays invisible must say so here, not leave the doctor
        check to be the first to notice."""
        seen = {"n": 0}

        def fake_which(name):
            if name == "uv":
                return "/usr/bin/uv"
            # adversarial: absent before AND after the install
            seen["n"] += 1
            return None

        with patch.object(_project_module.shutil, "which", side_effect=fake_which):
            with patch.object(_project_module, "subprocess") as mock_sub:
                mock_sub.TimeoutExpired = subprocess.TimeoutExpired
                mock_sub.run.return_value = MagicMock(returncode=0, stderr="")
                _project_module._ensure_adversarial_cli(project_with_pin)

        out = capsys.readouterr().out
        assert "not on your PATH" in out
        assert ".local/bin" in out

    def test_no_pin_anywhere_instructs_instead_of_installing_latest(
        self, tmp_path, capsys
    ):
        """No readable pin → instruct, never unpinned-latest (KIT-0068 A08:
        a silent fallback installed a five-versions-old library)."""
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "config.yml").write_text(
            "task_directory: .kit/tasks/\n", encoding="utf-8"
        )
        which = {"adversarial": None, "uv": "/usr/bin/uv"}
        with patch.object(
            _project_module.shutil, "which", side_effect=lambda n: which.get(n)
        ):
            with patch.object(
                _project_module, "_get_adversarial_cli_version", return_value=None
            ):
                with patch.object(_project_module, "subprocess") as mock_sub:
                    _project_module._ensure_adversarial_cli(tmp_path)
                    mock_sub.run.assert_not_called()
        assert (
            "Could not read the adversarial CLI version pin" in capsys.readouterr().out
        )


class TestAdversarialCliPinReader:
    """The pin's canonical home is .adversarial/config.yml (KIT-0083 F3).

    Every test here controls the mirror to a KNOWN, DISTINCT value via
    the fixture below. Asserting against the real repo's pyproject made
    two of these unfalsifiable: a precedence test whose two sources hold
    the SAME value cannot detect inverted precedence, and a
    `!= "0.0.1"` assertion is satisfied by None — so it passed even for
    a reader that returned nothing for every input (CodeRabbit round 1).
    """

    MIRROR_VERSION = "7.7.7"

    @pytest.fixture
    def mirror_root(self, tmp_path):
        """A fake kit root whose pyproject mirror pins MIRROR_VERSION.

        The reader locates pyproject relative to its own __file__, so
        the fixture returns a path to patch that with.
        """
        fake_root = tmp_path / "root"
        (fake_root / "scripts" / "core").mkdir(parents=True)
        fake_script = fake_root / "scripts" / "core" / "project"
        fake_script.write_text("", encoding="utf-8")
        (fake_root / "pyproject.toml").write_text(
            "[project]\ndependencies = "
            f'["adversarial-workflow=={self.MIRROR_VERSION}"]\n',
            encoding="utf-8",
        )
        return fake_script

    def test_reads_config_yml_pin(self, tmp_path, mirror_root):
        adv = tmp_path / ".adversarial"
        adv.mkdir()
        (adv / "config.yml").write_text(
            'adversarial_cli_version: "1.2.3"\n', encoding="utf-8"
        )
        with patch.dict(_project_module.__dict__, {"__file__": str(mirror_root)}):
            assert _project_module._get_adversarial_cli_version(tmp_path) == "1.2.3"

    def test_config_yml_wins_over_pyproject_mirror(self, tmp_path, mirror_root):
        """config.yml is canonical; pyproject is only a mirror.

        The two sources hold DIFFERENT values, so inverted precedence
        fails this test instead of silently passing it.
        """
        adv = tmp_path / ".adversarial"
        adv.mkdir()
        (adv / "config.yml").write_text(
            'adversarial_cli_version: "9.9.9"\n', encoding="utf-8"
        )
        with patch.dict(_project_module.__dict__, {"__file__": str(mirror_root)}):
            got = _project_module._get_adversarial_cli_version(tmp_path)
        assert got == "9.9.9", f"mirror won over the canonical home (got {got!r})"

    def test_planning_shape_without_config_pin_falls_back_to_pyproject(
        self, tmp_path, mirror_root
    ):
        """No config.yml pin → the mirror supplies the value."""
        (tmp_path / ".adversarial").mkdir()
        with patch.dict(_project_module.__dict__, {"__file__": str(mirror_root)}):
            got = _project_module._get_adversarial_cli_version(tmp_path)
        assert got == self.MIRROR_VERSION

    def test_commented_pin_is_not_read(self, tmp_path, mirror_root):
        """A commented-out example must never be read as the live pin.

        Asserts the mirror's exact value: `!= "0.0.1"` would also be
        satisfied by None, i.e. by a reader that found nothing at all.
        """
        adv = tmp_path / ".adversarial"
        adv.mkdir()
        (adv / "config.yml").write_text(
            '# adversarial_cli_version: "0.0.1"\ntask_directory: .kit/tasks/\n',
            encoding="utf-8",
        )
        with patch.dict(_project_module.__dict__, {"__file__": str(mirror_root)}):
            got = _project_module._get_adversarial_cli_version(tmp_path)
        assert (
            got == self.MIRROR_VERSION
        ), f"commented pin leaked, or fall-through broke (got {got!r})"


class TestInstallEvaluatorsEnsuresCli:
    """The CLI step must run even on the already-installed early return —
    'library present, CLI absent' IS the #103 shape (KIT-0083)."""

    def test_cli_ensured_before_already_installed_return(self, tmp_path, capsys):
        evaluators_dir = tmp_path / ".adversarial" / "evaluators"
        evaluators_dir.mkdir(parents=True)
        (evaluators_dir / ".installed-version").write_text(
            "v0.10.0 (abc12345)\n", encoding="utf-8"
        )

        with patch.object(_project_module, "_ensure_adversarial_cli") as ensure:
            with patch.object(_project_module, "subprocess") as mock_sub:
                mock_sub.TimeoutExpired = subprocess.TimeoutExpired
                mock_sub.run.return_value = MagicMock(returncode=0)
                _project_module.cmd_install_evaluators([], tmp_path)
            ensure.assert_called_once()

        assert "already installed" in capsys.readouterr().out


class TestAdversarialCliLiveness:
    """Presence is not liveness (o3 + fast-v2, converging finding).

    The install step must not print ✅ for a binary that `which` finds
    but that fails to run — the very next `project doctor` would FAIL on
    it, and the user would have two surfaces disagreeing about the same
    install.
    """

    def test_present_but_broken_binary_is_not_working(self):
        with patch.object(
            _project_module.shutil, "which", return_value="/usr/bin/adversarial"
        ):
            with patch.object(_project_module, "subprocess") as mock_sub:
                mock_sub.TimeoutExpired = subprocess.TimeoutExpired
                mock_sub.run.return_value = MagicMock(returncode=1)
                assert _project_module._adversarial_cli_works() is False

    def test_noisy_stderr_with_exit_zero_is_working(self):
        """A healthy CLI prints 'Unknown fields in evaluator.yml' to
        stderr — exit code is the signal, not output."""
        with patch.object(
            _project_module.shutil, "which", return_value="/usr/bin/adversarial"
        ):
            with patch.object(_project_module, "subprocess") as mock_sub:
                mock_sub.TimeoutExpired = subprocess.TimeoutExpired
                mock_sub.run.return_value = MagicMock(
                    returncode=0, stderr="Unknown fields in evaluator.yml: status"
                )
                assert _project_module._adversarial_cli_works() is True

    def test_hanging_binary_is_not_working(self):
        with patch.object(
            _project_module.shutil, "which", return_value="/usr/bin/adversarial"
        ):
            with patch.object(_project_module, "subprocess") as mock_sub:
                mock_sub.TimeoutExpired = subprocess.TimeoutExpired
                mock_sub.run.side_effect = subprocess.TimeoutExpired(
                    cmd="adversarial --version", timeout=30
                )
                assert _project_module._adversarial_cli_works() is False

    def test_absent_binary_is_not_working(self):
        with patch.object(_project_module.shutil, "which", return_value=None):
            assert _project_module._adversarial_cli_works() is False

    def test_broken_existing_cli_triggers_install_not_false_ok(self, tmp_path):
        """The whole point: a broken CLI already on PATH must NOT
        short-circuit the install step with a ✅."""
        adv = tmp_path / ".adversarial"
        adv.mkdir()
        (adv / "config.yml").write_text(
            'adversarial_cli_version: "1.0.1"\n', encoding="utf-8"
        )
        with patch.object(
            _project_module, "_adversarial_cli_works", return_value=False
        ):
            with patch.object(
                _project_module.shutil, "which", side_effect=lambda n: "/usr/bin/uv"
            ):
                with patch.object(_project_module, "subprocess") as mock_sub:
                    mock_sub.TimeoutExpired = subprocess.TimeoutExpired
                    mock_sub.run.return_value = MagicMock(returncode=0, stderr="")
                    _project_module._ensure_adversarial_cli(tmp_path)
                    # It attempted the install rather than returning early
                    assert mock_sub.run.called

    def test_post_install_broken_binary_advises_reinstall_not_path(
        self, tmp_path, capsys
    ):
        """uv exits 0 but the binary doesn't run: the remedy is
        --force reinstall, NOT a PATH change (three states, three
        messages)."""
        adv = tmp_path / ".adversarial"
        adv.mkdir()
        (adv / "config.yml").write_text(
            'adversarial_cli_version: "1.0.1"\n', encoding="utf-8"
        )
        which = {"adversarial": "/usr/bin/adversarial", "uv": "/usr/bin/uv"}
        with patch.object(
            _project_module, "_adversarial_cli_works", return_value=False
        ):
            with patch.object(
                _project_module.shutil, "which", side_effect=lambda n: which.get(n)
            ):
                with patch.object(_project_module, "subprocess") as mock_sub:
                    mock_sub.TimeoutExpired = subprocess.TimeoutExpired
                    mock_sub.run.return_value = MagicMock(returncode=0, stderr="")
                    _project_module._ensure_adversarial_cli(tmp_path)
        out = capsys.readouterr().out
        assert "not runnable" in out
        assert "--force" in out
        assert "export PATH" not in out


class TestPyprojectMirrorPinForms:
    """The mirror must read every pin form pyproject may carry — matching
    only '>=' would read an exact pin as 'no pin' and send an installable
    project down the instruct-only path (o3 review). KIT-0079 may write
    an exact pin here.

    Drives the REAL reader (not a re-implemented regex): the mirror is
    located relative to the script's own __file__, so the fixture builds
    a throwaway tree and points __file__ at it.
    """

    @pytest.mark.parametrize(
        "spec,expected",
        [
            ('"adversarial-workflow>=1.0.1",', "1.0.1"),
            ('"adversarial-workflow==1.2.3",', "1.2.3"),
            ('"adversarial-workflow~=1.2",', "1.2"),
            ('"adversarial-workflow >= 2.0.0",', "2.0.0"),
        ],
    )
    def test_pin_forms_are_read(self, tmp_path, spec, expected):
        # Mirror the real layout: <root>/scripts/core/project
        fake_root = tmp_path / "root"
        (fake_root / "scripts" / "core").mkdir(parents=True)
        fake_script = fake_root / "scripts" / "core" / "project"
        fake_script.write_text("", encoding="utf-8")
        (fake_root / "pyproject.toml").write_text(
            f"[project]\ndependencies = [\n    {spec}\n]\n", encoding="utf-8"
        )

        # A project dir with .adversarial/ but NO config.yml pin, so the
        # reader must fall through to the pyproject mirror.
        project_dir = tmp_path / "proj"
        (project_dir / ".adversarial").mkdir(parents=True)

        with patch.dict(_project_module.__dict__, {"__file__": str(fake_script)}):
            got = _project_module._get_adversarial_cli_version(project_dir)
        assert got == expected, f"pin form {spec!r} read as {got!r}, want {expected!r}"

    def test_absent_dependency_reads_as_no_pin(self, tmp_path):
        """No adversarial-workflow line at all → None, which callers turn
        into instruct-don't-install (never unpinned latest)."""
        fake_root = tmp_path / "root"
        (fake_root / "scripts" / "core").mkdir(parents=True)
        fake_script = fake_root / "scripts" / "core" / "project"
        fake_script.write_text("", encoding="utf-8")
        (fake_root / "pyproject.toml").write_text(
            '[project]\ndependencies = ["pytest>=8.0"]\n', encoding="utf-8"
        )
        project_dir = tmp_path / "proj"
        (project_dir / ".adversarial").mkdir(parents=True)
        with patch.dict(_project_module.__dict__, {"__file__": str(fake_script)}):
            assert _project_module._get_adversarial_cli_version(project_dir) is None


class TestPinValidation:
    """A hand-edited config.yml can hold anything; a junk pin must fail
    CLEARLY rather than becoming 'adversarial-workflow==--force' and
    surfacing as a baffling uv error (claude-code review).

    Not an injection concern: the pin is a list element to
    subprocess.run, never a shell string.
    """

    @pytest.mark.parametrize(
        "value,ok",
        [
            ("1.0.1", True),
            ("1.0.1rc1", True),
            ("2026.1.0", True),
            ("1.0.1-beta+build2", True),
            ("--force", False),
            ("$(whoami)", False),
            ("1.0.1;", False),
            ("", False),
            ("latest", False),
        ],
    )
    def test_version_like(self, value, ok):
        assert _project_module._is_version_like(value) is ok

    def test_junk_config_pin_does_not_reach_uv(self, tmp_path, capsys):
        """A junk pin must not be installed. It falls through to the
        pyproject mirror; with neither readable the caller instructs."""
        adv = tmp_path / ".adversarial"
        adv.mkdir()
        (adv / "config.yml").write_text(
            'adversarial_cli_version: "--force"\n', encoding="utf-8"
        )
        fake_root = tmp_path / "root"
        (fake_root / "scripts" / "core").mkdir(parents=True)
        fake_script = fake_root / "scripts" / "core" / "project"
        fake_script.write_text("", encoding="utf-8")
        (fake_root / "pyproject.toml").write_text(
            '[project]\ndependencies = ["pytest>=8.0"]\n', encoding="utf-8"
        )
        with patch.dict(_project_module.__dict__, {"__file__": str(fake_script)}):
            assert _project_module._get_adversarial_cli_version(tmp_path) is None


class TestGitGateDoesNotBlockCliInstall:
    """BugBot round 1: the git gate must not own the CLI path.

    doctor.d/31 tells users to run `install-evaluators` when the library
    is present but the CLI is missing. The CLI path needs only `uv` —
    never git — so a broken/absent git must not exit before the CLI step
    has even been attempted, or the doctor's advice cannot fix the thing
    it was recommended for.
    """

    @pytest.fixture
    def project_with_pin(self, tmp_path):
        adv = tmp_path / ".adversarial"
        adv.mkdir()
        (adv / "config.yml").write_text(
            'adversarial_cli_version: "1.0.1"\n', encoding="utf-8"
        )
        return tmp_path

    def test_cli_step_runs_before_git_gate(self, project_with_pin):
        """git --version returns non-zero → CLI step still ran."""
        with patch.object(_project_module, "_ensure_adversarial_cli") as ensure:
            with patch.object(_project_module, "subprocess") as mock_sub:
                mock_sub.TimeoutExpired = subprocess.TimeoutExpired
                mock_sub.run.return_value = MagicMock(returncode=1)  # git missing
                with pytest.raises(SystemExit):
                    _project_module.cmd_install_evaluators([], project_with_pin)
            ensure.assert_called_once()

    def test_absent_git_binary_prints_message_not_traceback(
        self, project_with_pin, capsys
    ):
        """A genuinely ABSENT git raises FileNotFoundError rather than
        returning non-zero. Without catching it the friendly message
        never prints and the user gets a raw traceback (found while
        reproducing the BugBot finding)."""
        with patch.object(_project_module, "_ensure_adversarial_cli"):
            with patch.object(_project_module, "subprocess") as mock_sub:
                mock_sub.TimeoutExpired = subprocess.TimeoutExpired
                mock_sub.run.side_effect = FileNotFoundError(2, "No such file", "git")
                with pytest.raises(SystemExit) as exc:
                    _project_module.cmd_install_evaluators([], project_with_pin)
                assert exc.value.code == 1
        assert "Git is required but not found" in capsys.readouterr().out

    def test_hung_git_probe_times_out_into_the_guidance_path(
        self, project_with_pin, capsys
    ):
        """A wedged git (prompting credential helper, hung filesystem)
        must time out into the same guidance, not hang the installer
        forever (CodeRabbit round 2)."""
        with patch.object(_project_module, "_ensure_adversarial_cli"):
            with patch.object(_project_module, "subprocess") as mock_sub:
                mock_sub.TimeoutExpired = subprocess.TimeoutExpired
                mock_sub.run.side_effect = subprocess.TimeoutExpired(
                    cmd="git --version", timeout=20
                )
                with pytest.raises(SystemExit) as exc:
                    _project_module.cmd_install_evaluators([], project_with_pin)
                assert exc.value.code == 1
        assert "Git is required but not found" in capsys.readouterr().out

    def test_git_probe_is_bounded_and_stdin_closed(self, project_with_pin):
        """The git probe carries the same bound and stdin handling as the
        CLI probe — an unbounded one hangs install-evaluators."""
        with patch.object(_project_module, "_ensure_adversarial_cli"):
            with patch.object(_project_module, "subprocess") as mock_sub:
                mock_sub.TimeoutExpired = subprocess.TimeoutExpired
                mock_sub.DEVNULL = subprocess.DEVNULL
                mock_sub.run.return_value = MagicMock(returncode=1)
                with pytest.raises(SystemExit):
                    _project_module.cmd_install_evaluators([], project_with_pin)
                kwargs = mock_sub.run.call_args.kwargs
        assert kwargs.get("timeout") == _project_module.CLI_PROBE_TIMEOUT
        assert kwargs.get("stdin") == subprocess.DEVNULL

    def test_cli_install_attempted_when_git_absent_but_uv_present(
        self, project_with_pin, capsys
    ):
        """The whole point of the reorder: git broken, uv fine → the CLI
        genuinely installs instead of being skipped."""
        which = {"adversarial": None, "uv": "/usr/bin/uv"}
        calls = []

        def fake_run(cmd, *a, **k):
            calls.append(cmd)
            if cmd[0] == "git":
                raise FileNotFoundError(2, "No such file", "git")
            return MagicMock(returncode=0, stderr="")

        with patch.object(
            _project_module.shutil, "which", side_effect=lambda n: which.get(n)
        ):
            with patch.object(_project_module, "subprocess") as mock_sub:
                mock_sub.TimeoutExpired = subprocess.TimeoutExpired
                mock_sub.run.side_effect = fake_run
                with pytest.raises(SystemExit):
                    _project_module.cmd_install_evaluators([], project_with_pin)

        assert ["uv", "tool", "install", "adversarial-workflow==1.0.1"] in calls


def _assert_no_library_state_claim(output):
    """Fail if `output` asserts anything about the LIBRARY's install state.

    One shared assertion for both call sites. Rejecting a single literal
    per test (e.g. only "library is installed" in one and only "still
    installed" in the other) let each test pass on the OTHER's wording —
    so swapping the two messages kept both green (CodeRabbit round 4).

    A regex rather than `==` on whole lines: the guarantee here is
    "makes no claim of this KIND", which a fixed expected string cannot
    express — any new phrasing would silently escape it. Substring/regex
    matching is justified for that reason (DK rules require the
    justification, not the avoidance).

    Covers plural agreement ("have been") and NEGATED forms ("has not
    been installed") — a negative statement about the library's state is
    still a statement about it, and equally outside what this step can
    know (CodeRabbit round 5).
    """
    claim = re.search(
        r"\blibrar(?:y|ies)\b[^\n]*\b(?:is|are|was|were|remains?|still|"
        r"already|(?:has|have)(?:\s+not)?\s+been)\b",
        output,
        re.IGNORECASE,
    )
    assert not claim, (
        "the CLI step claimed something about the library's state: "
        f"{claim.group(0)!r}"
    )


class TestNoLibraryStateClaimHelper:
    """The shared assertion's own coverage.

    It is the only thing standing between a reordered install step and a
    message that lies about state, so its blind spots matter as much as
    the messages it guards (CodeRabbit rounds 4-5).
    """

    @pytest.mark.parametrize(
        "message",
        [
            "The evaluator library is installed, but running an",
            "CLI install failed — the evaluator library is still installed",
            "the evaluator library is already installed",
            "the library remains installed",
            "The Library Was Installed",
            "evaluator libraries are installed",
            # plural agreement + negated forms: a negative claim about the
            # library's state is still a claim (CodeRabbit round 5)
            "the libraries have been installed",
            "the library has been installed",
            "the library has not been installed",
            "the libraries have not been installed",
        ],
    )
    def test_rejects_state_claims(self, message):
        with pytest.raises(AssertionError):
            _assert_no_library_state_claim(message)

    @pytest.mark.parametrize(
        "message",
        [
            "Running an evaluation needs the CLI. Install uv, then run:",
            "CLI install failed — continuing with the library install",
            "uv tool install adversarial-workflow==1.0.1",
            "Retry manually: uv tool install adversarial-workflow==1.0.1",
            "   uv: https://docs.astral.sh/uv/getting-started/installation/",
        ],
    )
    def test_allows_messages_that_claim_nothing(self, message):
        _assert_no_library_state_claim(message)


class TestCliStepMakesNoLibraryClaims:
    """The CLI step runs BEFORE the git gate and the library clone, so it
    cannot assert anything about the library's state.

    Those messages were written when the CLI step ran last, where the
    claim was true. The reorder (BugBot round 1) falsified them: with git
    absent, `install-evaluators` printed 'the evaluator library is
    installed' and then exited having installed nothing at all
    (CodeRabbit round 3).
    """

    @pytest.fixture
    def project_with_pin(self, tmp_path):
        adv = tmp_path / ".adversarial"
        adv.mkdir()
        (adv / "config.yml").write_text(
            'adversarial_cli_version: "1.0.1"\n', encoding="utf-8"
        )
        return tmp_path

    def test_uv_missing_message_claims_nothing_about_the_library(
        self, project_with_pin, capsys
    ):
        with patch.object(_project_module.shutil, "which", return_value=None):
            with patch.object(_project_module, "subprocess") as mock_sub:
                mock_sub.TimeoutExpired = subprocess.TimeoutExpired
                _project_module._ensure_adversarial_cli(project_with_pin)
        out = capsys.readouterr().out
        assert "uv tool install adversarial-workflow==1.0.1" in out
        _assert_no_library_state_claim(out)

    def test_install_failure_message_claims_nothing_about_the_library(
        self, project_with_pin, capsys
    ):
        which = {"adversarial": None, "uv": "/usr/bin/uv"}
        with patch.object(
            _project_module.shutil, "which", side_effect=lambda n: which.get(n)
        ):
            with patch.object(_project_module, "subprocess") as mock_sub:
                mock_sub.TimeoutExpired = subprocess.TimeoutExpired
                mock_sub.DEVNULL = subprocess.DEVNULL
                mock_sub.run.return_value = MagicMock(returncode=1, stderr="boom")
                _project_module._ensure_adversarial_cli(project_with_pin)
        out = capsys.readouterr().out
        assert "Retry manually" in out
        _assert_no_library_state_claim(out)
