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
