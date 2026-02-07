"""
Shared pytest fixtures and utilities for the agentive-starter-kit test suite.
"""

import shutil
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

# Get project root for accessing templates and launchers
PROJECT_ROOT = Path(__file__).parent.parent


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
    module: Any, tmp_path: Path, *, venv_exists: bool = False
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


def setup_temp_project(
    tmp_path: Path,
    *,
    include_template: bool = True,
    include_logs_dir: bool = True,
) -> None:
    """Set up a minimal temporary project structure for testing.

    This is a shared utility for agent creation tests.

    Args:
        tmp_path: Temporary directory path.
        include_template: Whether to include the agent template.
        include_logs_dir: Whether to create logs directory.
    """
    # Create directory structure
    agents_dir = tmp_path / ".claude" / "agents"
    agents_dir.mkdir(parents=True)

    launcher_dir = tmp_path / "agents"
    launcher_dir.mkdir(parents=True)

    if include_logs_dir:
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir(parents=True)

    # Copy template if needed
    if include_template:
        template_src = PROJECT_ROOT / ".claude" / "agents" / "AGENT-TEMPLATE.md"
        if template_src.exists():
            shutil.copy(template_src, agents_dir / "AGENT-TEMPLATE.md")
        else:
            # Create minimal template for testing
            (agents_dir / "AGENT-TEMPLATE.md").write_text(
                """---
name: [agent-name]
description: [One sentence description of agent role and primary responsibility]
model: claude-sonnet-4-20250514
tools:
  - Read
  - Write
---

# [Agent Name] Agent

You are a specialized [role description] agent.
"""
            )

    # Copy launcher or create minimal version
    launcher_src = PROJECT_ROOT / "agents" / "launch"
    if launcher_src.exists():
        shutil.copy(launcher_src, launcher_dir / "launch")
    else:
        # Create minimal launcher for testing
        # Note: No 'local' keyword at top level (only valid inside functions)
        (launcher_dir / "launch").write_text(
            """#!/bin/bash
# Minimal test launcher

agent_order=(
    "planner"
    "feature-developer"
)

serena_agents=(
    "planner"
    "feature-developer"
)

get_agent_icon() {
    local name="$1"
    local icon="⚡"
    [[ "$name" == *"planner"* ]] && icon="📋"
    echo "$icon"
}
"""
        )

    # Make launcher executable
    (launcher_dir / "launch").chmod(0o755)
