"""
Tests for UV Detection and Auto-Venv Creation
==============================================

TDD tests for ASK-0032: UV auto-detection for Python version management.

These tests verify:
1. detect_uv() correctly identifies uv availability
2. create_venv_with_uv() creates venvs using uv
3. Integration: setup uses uv when Python 3.13+ detected
4. Fallback: improved error message when uv not available
5. No regression: Python 3.10-3.12 behavior unchanged
"""

import importlib.util
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from conftest import MockVersionInfo, mock_project_path

# Load the project script as a module (same pattern as test_project_script.py)
_script_path = Path(__file__).parent.parent / "scripts" / "project"
_spec = importlib.util.spec_from_loader("project_script", loader=None)
_project_module = importlib.util.module_from_spec(_spec)

with open(_script_path) as f:
    _project_module.__dict__["__file__"] = str(_script_path)
    exec(f.read(), _project_module.__dict__)


class TestDetectUv:
    """Tests for detect_uv() function."""

    def test_detect_uv_when_installed(self, monkeypatch):
        """Should return True when uv is in PATH."""
        detect_uv = _project_module.detect_uv

        # Mock shutil.which to return a path for uv
        monkeypatch.setattr(
            _project_module.shutil,
            "which",
            lambda x: "/usr/local/bin/uv" if x == "uv" else None,
        )

        assert detect_uv() is True

    def test_detect_uv_when_not_installed(self, monkeypatch):
        """Should return False when uv is not in PATH."""
        detect_uv = _project_module.detect_uv

        # Mock shutil.which to return None for uv
        monkeypatch.setattr(_project_module.shutil, "which", lambda x: None)

        assert detect_uv() is False

    def test_detect_uv_only_checks_uv_binary(self, monkeypatch):
        """Should only check for 'uv', not other tools."""
        detect_uv = _project_module.detect_uv

        # Track what was queried
        queries = []

        def mock_which(cmd):
            queries.append(cmd)
            return "/usr/local/bin/uv" if cmd == "uv" else None

        monkeypatch.setattr(_project_module.shutil, "which", mock_which)

        detect_uv()

        assert queries == ["uv"]


class TestCreateVenvWithUv:
    """Tests for create_venv_with_uv() function."""

    def test_create_venv_with_uv_success(self, tmp_path):
        """Should return True when uv venv creation succeeds."""
        create_venv_with_uv = _project_module.create_venv_with_uv

        venv_dir = tmp_path / ".venv"

        with patch.object(_project_module, "subprocess") as mock_subprocess:
            mock_subprocess.TimeoutExpired = subprocess.TimeoutExpired
            mock_subprocess.run.return_value = MagicMock(
                returncode=0, stdout="", stderr=""
            )

            result = create_venv_with_uv(venv_dir, "3.12")

        assert result is True
        # Verify the correct command was called
        mock_subprocess.run.assert_called_once()
        call_args = mock_subprocess.run.call_args
        assert "uv" in call_args[0][0]
        assert "venv" in call_args[0][0]
        assert "--python" in call_args[0][0]
        assert "3.12" in call_args[0][0]

    def test_create_venv_with_uv_failure(self, tmp_path):
        """Should return False when uv venv creation fails."""
        create_venv_with_uv = _project_module.create_venv_with_uv

        venv_dir = tmp_path / ".venv"

        with patch.object(_project_module, "subprocess") as mock_subprocess:
            mock_subprocess.TimeoutExpired = subprocess.TimeoutExpired
            mock_subprocess.run.return_value = MagicMock(
                returncode=1, stdout="", stderr="Python 3.12 not found"
            )

            result = create_venv_with_uv(venv_dir, "3.12")

        assert result is False

    def test_create_venv_with_uv_handles_exception(self, tmp_path):
        """Should return False and not raise when subprocess fails."""
        create_venv_with_uv = _project_module.create_venv_with_uv

        venv_dir = tmp_path / ".venv"

        with patch.object(_project_module, "subprocess") as mock_subprocess:
            mock_subprocess.TimeoutExpired = subprocess.TimeoutExpired
            mock_subprocess.run.side_effect = OSError("uv not executable")

            result = create_venv_with_uv(venv_dir, "3.12")

        assert result is False

    def test_create_venv_with_uv_handles_timeout(self, tmp_path, capsys):
        """Should return False and print timeout message when uv times out."""
        create_venv_with_uv = _project_module.create_venv_with_uv

        venv_dir = tmp_path / ".venv"

        with patch.object(_project_module, "subprocess") as mock_subprocess:
            mock_subprocess.TimeoutExpired = subprocess.TimeoutExpired
            mock_subprocess.run.side_effect = subprocess.TimeoutExpired(
                cmd="uv venv", timeout=600
            )

            result = create_venv_with_uv(venv_dir, "3.12")

        assert result is False

        captured = capsys.readouterr()
        assert "timed out" in captured.out.lower()
        assert "600" in captured.out

    def test_create_venv_with_uv_default_version(self, tmp_path):
        """Should default to Python 3.12 if no version specified."""
        create_venv_with_uv = _project_module.create_venv_with_uv

        venv_dir = tmp_path / ".venv"

        with patch.object(_project_module, "subprocess") as mock_subprocess:
            mock_subprocess.TimeoutExpired = subprocess.TimeoutExpired
            mock_subprocess.run.return_value = MagicMock(
                returncode=0, stdout="", stderr=""
            )

            create_venv_with_uv(venv_dir)  # No version specified

        call_args = mock_subprocess.run.call_args
        assert "3.12" in call_args[0][0]


class TestSetupWithUvIntegration:
    """Integration tests for setup command with uv detection."""

    def test_python313_with_uv_creates_venv(self, capsys, tmp_path):
        """Python 3.13 with uv available should auto-create 3.12 venv."""
        cmd_setup = _project_module.cmd_setup

        # Mock Python 3.13
        mock_version = MockVersionInfo(3, 13, 0)

        # Track if create_venv_with_uv was called
        uv_venv_called = []

        def mock_create_venv_with_uv(venv_dir, python_version="3.12"):
            uv_venv_called.append((venv_dir, python_version))
            return True

        with patch.object(_project_module.sys, "version_info", mock_version):
            # Mock uv detection to return True
            with patch.object(_project_module, "detect_uv", return_value=True):
                # Mock create_venv_with_uv to succeed
                with patch.object(
                    _project_module, "create_venv_with_uv", mock_create_venv_with_uv
                ):
                    # Mock Path to use tmp_path (venv doesn't exist yet)
                    with mock_project_path(
                        _project_module, tmp_path, venv_exists=False
                    ):
                        # Mock subprocess for pip install
                        with patch.object(
                            _project_module, "subprocess"
                        ) as mock_subprocess:
                            mock_subprocess.run.return_value = MagicMock(
                                returncode=0, stderr=""
                            )

                            try:
                                cmd_setup([])
                            except SystemExit:
                                pass

        captured = capsys.readouterr()

        # Should have called create_venv_with_uv
        assert len(uv_venv_called) == 1
        assert uv_venv_called[0][1] == "3.12"  # Should use Python 3.12

        # Should show appropriate message
        assert "uv" in captured.out.lower()
        assert "3.12" in captured.out

    def test_python313_without_uv_shows_improved_error(self, capsys):
        """Python 3.13 without uv should show improved error with uv recommendation."""
        cmd_setup = _project_module.cmd_setup

        # Mock Python 3.13
        mock_version = MockVersionInfo(3, 13, 7)

        with patch.object(_project_module.sys, "version_info", mock_version):
            # Mock uv detection to return False
            with patch.object(_project_module, "detect_uv", return_value=False):
                with pytest.raises(SystemExit) as exc_info:
                    cmd_setup([])

                assert exc_info.value.code == 1

        captured = capsys.readouterr()

        # Should show version not supported
        assert "3.13.7" in captured.out
        assert "not yet supported" in captured.out or "not supported" in captured.out

        # Should recommend uv as primary solution
        assert "uv" in captured.out
        assert "curl" in captured.out or "astral.sh" in captured.out

        # Should still show alternative options
        assert "pyenv" in captured.out
        assert "brew" in captured.out

    def test_python313_uv_venv_creation_fails_shows_error(self, capsys, tmp_path):
        """If uv venv creation fails, should show helpful error."""
        cmd_setup = _project_module.cmd_setup

        # Mock Python 3.13
        mock_version = MockVersionInfo(3, 13, 0)

        with patch.object(_project_module.sys, "version_info", mock_version):
            # Mock uv detection to return True
            with patch.object(_project_module, "detect_uv", return_value=True):
                # Mock create_venv_with_uv to fail
                with patch.object(
                    _project_module, "create_venv_with_uv", return_value=False
                ):
                    # Mock Path to use tmp_path
                    with mock_project_path(
                        _project_module, tmp_path, venv_exists=False
                    ):
                        with pytest.raises(SystemExit) as exc_info:
                            cmd_setup([])

                        assert exc_info.value.code == 1

        captured = capsys.readouterr()

        # Should show uv failed message
        assert "uv" in captured.out.lower()
        # Should suggest manual command
        assert "venv" in captured.out.lower()


class TestNoRegressionPython312:
    """Tests to ensure Python 3.10-3.12 behavior is unchanged."""

    def test_python312_does_not_use_uv(self, capsys, tmp_path):
        """Python 3.12 should use standard venv, not uv."""
        cmd_setup = _project_module.cmd_setup

        # Mock Python 3.12
        mock_version = MockVersionInfo(3, 12, 4)

        # Track if detect_uv was called
        detect_uv_called = []

        def mock_detect_uv() -> bool:
            detect_uv_called.append(True)
            return True  # Even if uv is available, shouldn't be used

        with patch.object(_project_module.sys, "version_info", mock_version):
            with patch.object(_project_module, "detect_uv", mock_detect_uv):
                # Mock Path (venv exists) and subprocess
                with mock_project_path(_project_module, tmp_path, venv_exists=True):
                    with patch.object(_project_module, "subprocess") as mock_subprocess:
                        mock_subprocess.TimeoutExpired = subprocess.TimeoutExpired
                        mock_subprocess.run.return_value = MagicMock(
                            returncode=0, stderr=""
                        )

                        try:
                            cmd_setup([])
                        except SystemExit:
                            pass

        captured = capsys.readouterr()

        # detect_uv should NOT have been called for Python 3.12
        assert len(detect_uv_called) == 0

        # Should show normal version accepted message
        assert "3.12.4" in captured.out
        assert "too old" not in captured.out
        assert "not yet supported" not in captured.out

    def test_python310_proceeds_normally(self, capsys, tmp_path):
        """Python 3.10 should proceed with normal venv creation."""
        cmd_setup = _project_module.cmd_setup

        # Mock Python 3.10
        mock_version = MockVersionInfo(3, 10, 12)

        with patch.object(_project_module.sys, "version_info", mock_version):
            with mock_project_path(_project_module, tmp_path, venv_exists=True):
                with patch.object(_project_module, "subprocess") as mock_subprocess:
                    mock_subprocess.TimeoutExpired = subprocess.TimeoutExpired
                    mock_subprocess.run.return_value = MagicMock(
                        returncode=0, stderr=""
                    )

                    try:
                        cmd_setup([])
                    except SystemExit:
                        pass

        captured = capsys.readouterr()

        # Should proceed normally
        assert "3.10.12" in captured.out
        assert "too old" not in captured.out
        assert "not yet supported" not in captured.out


class TestEdgeCases:
    """Edge case tests for uv detection and venv creation."""

    def test_detect_uv_checks_path_presence(self, monkeypatch):
        """Verify detect_uv() returns True when uv is present in PATH."""
        detect_uv = _project_module.detect_uv

        # shutil.which returns path when uv is found
        monkeypatch.setattr(
            _project_module.shutil, "which", lambda x: "/usr/local/bin/uv"
        )

        # detect_uv should return True (it checks PATH presence)
        assert detect_uv() is True

    def test_create_venv_with_uv_with_custom_version(self, tmp_path):
        """Should support custom Python version."""
        create_venv_with_uv = _project_module.create_venv_with_uv

        venv_dir = tmp_path / ".venv"

        with patch.object(_project_module, "subprocess") as mock_subprocess:
            mock_subprocess.TimeoutExpired = subprocess.TimeoutExpired
            mock_subprocess.run.return_value = MagicMock(
                returncode=0, stdout="", stderr=""
            )

            create_venv_with_uv(venv_dir, "3.11")

        call_args = mock_subprocess.run.call_args
        assert "3.11" in call_args[0][0]

    def test_python314_also_tries_uv(self, tmp_path):
        """Future Python versions (3.14+) should also try uv."""
        cmd_setup = _project_module.cmd_setup

        # Mock Python 3.14
        mock_version = MockVersionInfo(3, 14, 0)

        uv_venv_called = []

        def mock_create_venv_with_uv(venv_dir, python_version="3.12"):
            uv_venv_called.append((venv_dir, python_version))
            return True

        with patch.object(_project_module.sys, "version_info", mock_version):
            with patch.object(_project_module, "detect_uv", return_value=True):
                with patch.object(
                    _project_module, "create_venv_with_uv", mock_create_venv_with_uv
                ):
                    with mock_project_path(
                        _project_module, tmp_path, venv_exists=False
                    ):
                        with patch.object(
                            _project_module, "subprocess"
                        ) as mock_subprocess:
                            mock_subprocess.run.return_value = MagicMock(
                                returncode=0, stderr=""
                            )

                            try:
                                cmd_setup([])
                            except SystemExit:
                                pass

        # Should have called create_venv_with_uv
        assert len(uv_venv_called) == 1
