"""
Shared pytest fixtures and utilities for the agentive-starter-kit test suite.
"""

import pytest


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

    def __init__(self, major: int, minor: int, micro: int):
        self.major = major
        self.minor = minor
        self.micro = micro
        self._tuple = (major, minor, micro)

    def __lt__(self, other):
        if isinstance(other, tuple):
            return self._tuple[: len(other)] < other
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, tuple):
            return self._tuple[: len(other)] >= other
        return NotImplemented

    def __getitem__(self, key):
        return self._tuple[key]

    def __repr__(self):
        return f"MockVersionInfo({self.major}, {self.minor}, {self.micro})"
