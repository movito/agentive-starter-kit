"""
Shared pytest fixtures and utilities for the agentive-starter-kit test suite.
"""

import shutil
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

# Project root for locating real files used by test fixtures
PROJECT_ROOT = Path(__file__).resolve().parent.parent


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


# ---------------------------------------------------------------------------
# Minimal fallback launcher for test environments
# Must be valid bash: `local` only inside functions (fixes T3 from bug ledger)
# ---------------------------------------------------------------------------
MINIMAL_LAUNCHER = r"""#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CLAUDE_AGENTS_DIR="$PROJECT_ROOT/.claude/agents"

get_agent_files() {
    local agent_order=(
        "planner"
    )
    local all_files=$(find "$CLAUDE_AGENTS_DIR" -name "*.md" \
        -not -name "AGENT-TEMPLATE.md")
    for agent_name in "${agent_order[@]}"; do
        for file in $all_files; do
            local base_name=$(basename "$file" .md)
            if [[ "$base_name" == "$agent_name" ]]; then
                echo "$file"
                break
            fi
        done
    done
}

needs_serena_activation() {
    local name="$1"
    local serena_agents=(
        "planner"
    )
    for sa in "${serena_agents[@]}"; do
        if [[ "$name" == "$sa" ]]; then
            return 0
        fi
    done
    return 1
}

get_agent_icon() {
    local name="$1"
    local icon="⚡"
    [[ "$name" == *"planner"* ]] && icon="📋"
    echo "$icon"
}
"""

# Minimal valid agent template for test environments
MINIMAL_TEMPLATE = """---
name: [agent-name]
description: [One sentence description of agent role and primary responsibility]
model: claude-sonnet-4-5-20250929
tools:
  - Read
  - Write
  - Edit
  - Bash
---

# [Agent Name] Agent

You are a specialized agent.
"""


def setup_temp_project(base_dir: Path | None = None) -> Path:
    """Create a temporary project directory structure for testing create-agent.sh.

    Creates:
        <temp_dir>/
            .claude/agents/AGENT-TEMPLATE.md  (real or fallback)
            agents/launch                      (real or fallback, executable)
            logs/                              (empty, for log output)

    Uses real project files when available, falls back to minimal valid
    versions when running in isolated environments (CI containers, etc.).

    Args:
        base_dir: Optional parent directory. If None, creates a new tempdir.

    Returns:
        Path to the temporary project root directory.
    """
    if base_dir is None:
        base_dir = Path(tempfile.mkdtemp(prefix="agent-test-"))

    # Create directory structure
    agents_dir = base_dir / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    claude_agents_dir = base_dir / ".claude" / "agents"
    claude_agents_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Copy or create AGENT-TEMPLATE.md
    real_template = PROJECT_ROOT / ".claude" / "agents" / "AGENT-TEMPLATE.md"
    dest_template = claude_agents_dir / "AGENT-TEMPLATE.md"
    if real_template.exists():
        shutil.copy2(real_template, dest_template)
    else:
        dest_template.write_text(MINIMAL_TEMPLATE)

    # Copy or create agents/launch
    real_launcher = PROJECT_ROOT / "agents" / "launch"
    dest_launcher = agents_dir / "launch"
    if real_launcher.exists():
        shutil.copy2(real_launcher, dest_launcher)
    else:
        dest_launcher.write_text(MINIMAL_LAUNCHER)
    dest_launcher.chmod(0o755)

    return base_dir
