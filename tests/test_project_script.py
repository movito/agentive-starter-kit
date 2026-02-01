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

# Load the project script as a module
_script_path = Path(__file__).parent.parent / "scripts" / "project"
_spec = importlib.util.spec_from_loader("project_script", loader=None)
_project_module = importlib.util.module_from_spec(_spec)

# Read and execute the script to get the functions
with open(_script_path) as f:
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
