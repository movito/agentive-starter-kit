"""
Shared pytest fixtures and utilities for the agentive-starter-kit test suite.
"""

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock, patch


class MockVersionInfo:
    """Mock sys.version_info that supports both tuple comparison and attribute access.

    This class mimics Python's sys.version_info behavior for testing version checks.
    It supports:
    - Attribute access: mock_version.major, mock_version.minor, mock_version.micro
    - Tuple comparison: mock_version < (3, 13), mock_version >= (3, 10)
    - Index access: mock_version[0], mock_version[1], mock_version[2]

    Example:
        mock_version = MockVersionInfo(3, 12, 4)
        assert mock_version.major == 3
        assert mock_version < (3, 13)
        assert mock_version[1] == 12
    """

    def __init__(self, major: int, minor: int, micro: int) -> None:
        self.major = major
        self.minor = minor
        self.micro = micro
        self._tuple = (major, minor, micro)

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, tuple):
            return self._tuple[: len(other)] < other
        return NotImplemented

    def __le__(self, other: Any) -> bool:
        if isinstance(other, tuple):
            return self._tuple[: len(other)] <= other
        return NotImplemented

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, tuple):
            return self._tuple[: len(other)] > other
        return NotImplemented

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, tuple):
            return self._tuple[: len(other)] >= other
        return NotImplemented

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, tuple):
            return self._tuple[: len(other)] == other
        return NotImplemented

    def __getitem__(self, key: int) -> int:
        return self._tuple[key]

    def __repr__(self) -> str:
        return f"MockVersionInfo({self.major}, {self.minor}, {self.micro})"


@contextmanager
def mock_project_path(
    module: Any, tmp_path: Path, venv_exists: bool = False
) -> Generator[MagicMock, None, None]:
    """Context manager that mocks Path for project script tests.

    This fixture creates a mock Path setup commonly needed when testing
    the project script's setup command. It mocks:
    - venv_dir.exists() to return venv_exists
    - Path division operations (__truediv__) to return the mock venv
    - str() conversion to return tmp_path / ".venv"
    - resolve().parent.parent to return a mock project dir

    Args:
        module: The project module to patch (e.g., _project_module)
        tmp_path: pytest tmp_path fixture for temporary directory
        venv_exists: Whether the mock venv should report as existing

    Yields:
        MagicMock: The mock Path class for additional assertions

    Example:
        with mock_project_path(module, tmp_path, venv_exists=False) as mp:
            cmd_setup([])
            # mp can be used for assertions if needed
    """
    with patch.object(module, "Path") as mock_path:
        mock_venv = MagicMock()
        mock_venv.exists.return_value = venv_exists
        mock_venv.__truediv__ = lambda self, x: mock_venv
        mock_venv.__str__ = lambda self: str(tmp_path / ".venv")

        # Create mock project_dir that returns mock_venv when divided
        # This ensures venv_dir.exists() uses mock_venv.exists(), not filesystem
        mock_project_dir = MagicMock()
        mock_project_dir.__truediv__ = lambda self, x: mock_venv

        mock_path.return_value.__truediv__ = lambda self, x: mock_venv
        mock_path.return_value.resolve.return_value.parent.parent = mock_project_dir
        yield mock_path
