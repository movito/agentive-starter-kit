"""Guard the behavioral contracts encoded in the agent definitions.

These contracts are prose in markdown files read at session time; nothing
else stops a future rewrite from silently dropping one — which is how
KIT-0083's session started in the primary clone on main (the agent
definition said `checkout -b`; the template said never), and how the
2.0.0 review found the evaluator ordering contradicting itself for three
task cycles. These greps make such a drop loud. If a rewrite legitimately
rewords a contract, update the sentinel strings here in the same PR.

Pinned so far:

- worktree topology — verify, never create (KIT-0088)
- evaluator runs before the PR opens (KIT-0097 F1)
- paired agents (`-f5` model-pin forks) share one body (KIT-0097)
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


@pytest.mark.parametrize("agent", FEATURE_DEVELOPERS)
def test_feature_developer_runs_evaluator_before_pr_open(agent):
    """The evaluator phase must precede the Ship phase (KIT-0097 F1).

    The pre-open trio rule has been the documented order since KIT-0035
    (widened KIT-0046), but the Workflow Overview table kept listing
    Evaluator *after* CI+Bots — so an agent following the table opened the
    PR first and burned a bot round on every evaluator-driven rewrite.
    BugBot rated it High on the 2.0.0 release review. Pin the ordering so
    a future rewrite cannot silently reintroduce it.
    """
    text = (REPO / agent).read_text(encoding="utf-8")

    # (declared phase number, document order) per heading. Tolerate extra
    # whitespace around the `##` and after the colon so a cosmetic edit
    # doesn't read as a missing phase.
    headings = [
        (int(num), position, title.strip())
        for position, (num, title) in enumerate(
            re.findall(r"^\s*##\s+Phase\s+(\d+):\s*(.+?)\s*$", text, re.MULTILINE)
        )
    ]

    def find(prefix):
        matches = [h for h in headings if h[2].startswith(prefix)]
        assert len(matches) <= 1, (
            f"{agent}: {len(matches)} phase headings start with {prefix!r} "
            f"({[h[2] for h in matches]}) — the order check would silently "
            "test whichever came first; give the phases distinct titles"
        )
        return matches[0] if matches else None

    evaluator, ship, bots = find("Evaluator"), find("Ship"), find("CI + Bot")

    assert evaluator is not None, f"{agent}: no '## Phase N: Evaluator' heading"
    assert ship is not None, f"{agent}: no '## Phase N: Ship' heading"
    assert bots is not None, f"{agent}: no '## Phase N: CI + Bot Review' heading"

    # Both the declared numbers and the document order must agree that the
    # trio comes first — an agent follows the numbers, a reader follows the
    # order, and a rewrite that breaks either reintroduces the defect.
    for axis, idx in (("declared phase number", 0), ("document order", 1)):
        assert evaluator[idx] < ship[idx] < bots[idx], (
            f"{agent}: by {axis} the phases run "
            f"Evaluator={evaluator[idx]}, Ship={ship[idx]}, CI+Bots={bots[idx]} "
            "— the trio must run BEFORE the PR opens "
            "(KIT-0035, widened KIT-0046; KIT-0097 F1)"
        )

    # The overview table drove the original defect — pin it too, not just
    # the section order.
    # Tolerant of indentation, bold markers and smart quotes around the
    # phrase — what must not change is that the row says it runs pre-PR.
    assert re.search(
        r"^\s*\|\s*\d+\.\s*Evaluator\s*\|[^|]*before PR open",
        text,
        re.MULTILINE | re.I,
    ), (
        f"{agent}: the Workflow Overview table's Evaluator row must state "
        "that it runs before PR open (KIT-0097 F1)"
    )


@pytest.mark.parametrize(
    "canonical,variant",
    [
        (FEATURE_DEVELOPERS[0], FEATURE_DEVELOPERS[1]),
        (PLANNERS[0], PLANNERS[1]),
    ],
)
def test_agent_pair_bodies_stay_identical(canonical, variant):
    """A pair's shared body must not drift (KIT-0097).

    The -f5 variants are model-pin forks: identical workflow, different
    `model:`. Every fix is supposed to land in both halves, and the
    2.0.0 review found defects that had been fixed in one copy only.
    Compare from the shared body onward, normalizing the one line that
    legitimately differs (the Response Format header).
    """
    marker = "## Workflow Overview"
    texts = {}
    for path in (canonical, variant):
        text = (REPO / path).read_text(encoding="utf-8")
        assert marker in text, f"{path}: no {marker!r} section to anchor the diff"
        body = text.split(marker, 1)[1]
        # The identity header carries the variant suffix by design.
        texts[path] = re.sub(
            r"\*\*[A-Z-]+(?:-F5)?\*\* \| Task:", "**AGENT** | Task:", body
        )

    assert texts[canonical] == texts[variant], (
        f"{canonical} and {variant} have drifted below {marker!r}. "
        "The pair shares one body — apply every edit to both halves "
        "(KIT-0097)."
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
