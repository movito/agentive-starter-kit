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

    def find(label, pattern):
        """Match the phase title exactly (modulo a trailing parenthetical).

        `startswith` would accept an unrelated future heading — 'Evaluator
        Notes' would satisfy a check meant for the Evaluator phase — so the
        selector is anchored instead.
        """
        rx = re.compile(pattern, re.I)
        matches = [h for h in headings if rx.fullmatch(h[2])]
        assert len(matches) == 1, (
            f"{agent}: expected exactly 1 phase heading matching {label!r}, "
            f"found {len(matches)} ({[h[2] for h in headings]}) — an order "
            "check against 0 or 2 matches proves nothing"
        )
        return matches[0]

    # The phase NAME is pinned exactly. Only a "(GATE)" marker and/or an
    # em-dash annotation may follow it — so "Evaluator Notes" does NOT
    # match, while "Evaluator (GATE) — before the PR opens" does.
    suffix = r"(?: \(GATE\))?(?: —.*)?"
    evaluator = find("Evaluator", rf"Evaluator{suffix}")
    ship = find("Ship", rf"Ship{suffix}")
    bots = find("CI + Bot Review", rf"CI \+ Bot Review{suffix}")

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
    # the section order. Scope to THE Workflow Overview table: a
    # document-wide search would be satisfied by a stale duplicate table
    # elsewhere while the real one had regressed.
    sections = text.split("## Workflow Overview")
    assert len(sections) == 2, (
        f"{agent}: expected exactly 1 '## Workflow Overview' heading, "
        f"found {len(sections) - 1} — the table assertion below needs an "
        "unambiguous target"
    )
    overview = sections[1].split("\n## ", 1)[0]

    rows = re.findall(
        r"^\s*\|\s*\d+\.\s*Evaluator\s*\|([^|]*)\|", overview, re.MULTILINE | re.I
    )
    assert len(rows) == 1, (
        f"{agent}: expected exactly 1 Evaluator row in the Workflow "
        f"Overview table, found {len(rows)}"
    )
    assert re.search(r"before PR open", rows[0], re.I), (
        f"{agent}: the Workflow Overview table's Evaluator row must state "
        f"that it runs before PR open (KIT-0097 F1) — got: {rows[0].strip()!r}"
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
