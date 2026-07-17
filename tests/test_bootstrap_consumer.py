"""Tests for scripts/local/engine-consumer.sh — KIT-LOCAL marker wiring.

KIT-0034 F5: every agent file carrying KIT-LOCAL markers must be wired into
the consumer engine twice — listed in KIT_AGENTS (drives the marker-merge
step and the --no-kit prune) and rsync-excluded in AGENT_EXCLUDES (so the
plain copy step never ships the kit's own filled-in regions to a consumer).
A marker-bearing agent missing from either list leaks kit identity into
fresh consumers (BugBot, PR #66) or survives a --no-kit opt-out (CodeRabbit,
PR #68). The bash arrays are text-parsed; the script is never executed.

KIT-0053 moved the implementation from the bootstrap-consumer.sh entrance
(now a shim over the setup door) to engine-consumer.sh — the arrays live
in the engine.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT_PATH = REPO_ROOT / "scripts" / "local" / "engine-consumer.sh"
_AGENTS_DIR = REPO_ROOT / ".claude" / "agents"

# engine-consumer.sh is an ASK-only bootstrap tool (scripts/local is not
# synced downstream). The consumer sync also excludes this test, but guard
# the load so a stray copy in a consumer checkout skips cleanly instead of
# erroring at collection.
if not _SCRIPT_PATH.exists():
    pytest.skip(
        "engine-consumer.sh present only in the kit repo",
        allow_module_level=True,
    )

_SCRIPT_TEXT = _SCRIPT_PATH.read_text(encoding="utf-8")

_MARKER_BEGIN = "<!-- BEGIN KIT-LOCAL:"


def _marker_bearing_agents() -> set[str]:
    """Basenames of .claude/agents/*.md files containing KIT-LOCAL markers."""
    return {
        p.name
        for p in _AGENTS_DIR.glob("*.md")
        if _MARKER_BEGIN in p.read_text(encoding="utf-8")
    }


def _kit_agents() -> set[str]:
    """Entries of the KIT_AGENTS=(...) bash array, text-parsed."""
    match = re.search(r"^KIT_AGENTS=\(([^)]*)\)", _SCRIPT_TEXT, re.MULTILINE)
    assert match is not None, "KIT_AGENTS array not found in engine-consumer.sh"
    return set(match.group(1).split())


def _agent_excludes() -> set[str]:
    """Filenames excluded via AGENT_EXCLUDES=(--exclude='...' ...).

    Assumes the array literal contains no nested parentheses (true of the
    controlled internal file; a format change fails the search loudly).
    """
    match = re.search(
        r"^AGENT_EXCLUDES=\((.*?)\)", _SCRIPT_TEXT, re.MULTILINE | re.DOTALL
    )
    assert match is not None, "AGENT_EXCLUDES array not found in engine-consumer.sh"
    return set(re.findall(r"--exclude='([^']+)'", match.group(1)))


class TestMarkerAgentMembership:
    def test_marker_agents_exist(self):
        # Guard against a silently green run if the marker convention moves.
        assert _marker_bearing_agents(), "no KIT-LOCAL marker-bearing agents found"

    def test_every_marker_agent_in_kit_agents(self):
        missing = _marker_bearing_agents() - _kit_agents()
        assert not missing, (
            f"KIT-LOCAL marker-bearing agents missing from KIT_AGENTS in "
            f"engine-consumer.sh (marker-merge + --no-kit prune skip them): "
            f"{sorted(missing)}"
        )

    def test_every_marker_agent_in_agent_excludes(self):
        missing = _marker_bearing_agents() - _agent_excludes()
        assert not missing, (
            f"KIT-LOCAL marker-bearing agents missing from AGENT_EXCLUDES in "
            f"engine-consumer.sh (plain rsync would ship kit-filled regions "
            f"to consumers): {sorted(missing)}"
        )

    def test_no_stale_kit_agents_entries(self):
        # An entry without markers means the agent was retired or de-markered
        # but the bootstrap wiring was not updated.
        stale = _kit_agents() - _marker_bearing_agents()
        assert not stale, (
            f"KIT_AGENTS entries with no KIT-LOCAL markers in .claude/agents/: "
            f"{sorted(stale)}"
        )


class TestConsumerTestsRsyncBoundary:
    """Tests reading scripts/local/ must not ship to consumers (F2 rule)."""

    # This module reads engine-consumer.sh itself, so it falls under the
    # same exclusion rule it enforces.
    EXCLUDED_TESTS = (
        "test_kit_markers.py",
        "test_bootstrap_consumer.py",
        "test_bootstrap_shapes.py",
        "test_check_hook_seeds.py",
        "test_entrance_shims.py",
        "test_setup_door.py",
    )

    def test_excluded_from_consumer_rsync(self):
        for name in self.EXCLUDED_TESTS:
            assert f"--exclude='{name}'" in _SCRIPT_TEXT, (
                f"{name} reads scripts/local/ content but is not rsync-excluded "
                f"from the consumer tests/ sync in engine-consumer.sh"
            )

    def test_stale_copy_swept_from_consumers(self):
        for name in self.EXCLUDED_TESTS:
            assert f'"$TARGET/tests/{name}"' in _SCRIPT_TEXT, (
                f"{name} has no rm -f sweep in engine-consumer.sh — a stale "
                f"copy from an earlier bootstrap would survive --ignore-existing"
            )
