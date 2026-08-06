"""Guard the worktree-topology contract in the agent definitions (KIT-0088).

The contract is prose in markdown files read at session time; nothing
else stops a future rewrite from silently dropping it — which is how
KIT-0083's session started in the primary clone on main (the agent
definition said `checkout -b`; the template said never). These greps
make that drop loud. If a rewrite legitimately rewords the contract,
update the sentinel strings here in the same PR.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

FEATURE_DEVELOPERS = [
    ".claude/agents/feature-developer.md",
    ".claude/agents/feature-developer-f5.md",
]
PLANNERS = [
    ".claude/agents/planner.md",
    ".claude/agents/planner-f5.md",
]

# A command line (not prose/comment) that creates a branch in place.
CREATE_IN_PLACE = re.compile(r"^\s*(GIT_TARGET|git)\s+checkout -b", re.MULTILINE)


@pytest.mark.parametrize("agent", FEATURE_DEVELOPERS)
def test_feature_developer_phase1_verifies_never_creates(agent):
    text = (REPO / agent).read_text(encoding="utf-8")
    assert (
        "VERIFY the worktree/branch, never create it" in text
    ), f"{agent}: Phase 1 topology contract sentinel missing (KIT-0088 F1)"
    phase1 = text.split("## Phase 1")[1].split("## Phase 2")[0]
    assert not CREATE_IN_PLACE.search(phase1), (
        f"{agent}: Phase 1 contains a checkout -b command — the branch is "
        "created at authoring time, sessions only verify (KIT-0088 F1)"
    )


@pytest.mark.parametrize("agent", PLANNERS)
def test_planner_requires_session_topology_in_handoffs(agent):
    text = (REPO / agent).read_text(encoding="utf-8")
    assert "Session topology (REQUIRED)" in text, (
        f"{agent}: Phase 4 handoff checklist must require a Session "
        "topology section (KIT-0088 F2)"
    )
    assert "never `checkout -b`" in text, (
        f"{agent}: Phase 5 must state branches are created at authoring "
        "time (KIT-0088 F5)"
    )
    assert "Rename the session to" in text, (
        f"{agent}: Phase 5 footer must carry the session-rename "
        "suggestion (operator convention, 2026-08-06)"
    )
