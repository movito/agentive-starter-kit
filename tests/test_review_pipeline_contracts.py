"""Drift greps for the KIT-0116 review pipeline (red-first).

The review ladder lives across instruction surfaces that nothing but
these greps holds together: the preflight command's gate count, the
Review Flags field, the REVIEW-PIPELINE.md value authority, and (from
Phase 2) the KIT-ADR-0036 read-only reviewer carve-out. Sibling of
``test_agent_contracts.py`` — same rationale: contracts are prose, and
a rewrite can silently drop one unless a grep makes it loud.

Written BEFORE the Phase-1 surface edits (spec Verification step 1) so
each assertion was observed RED against the pre-KIT-0116 tree.

Phase arming: the ADR-citation and Bash-absence checks assert against
KIT-ADR-0036, which Phase 2 creates. They skip while the ADR file is
absent and arm mechanically the moment it exists — so Tier 2 cannot
merge with non-compliant reviewer toolsets (spec Test Requirements,
deep-evaluator finding).
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

REVIEW_PIPELINE = ".kit/context/workflows/REVIEW-PIPELINE.md"
PREFLIGHT_CMD = ".claude/commands/preflight.md"
COMMIT_PUSH_PR_CMD = ".claude/commands/commit-push-pr.md"
STARTER_TEMPLATE = ".kit/templates/TASK-STARTER-TEMPLATE.md"
# Glob on the ADR NUMBER, not an exact slug — a slug variant
# ("read-only" vs "readonly") must arm the Phase-2 checks, not
# silently disarm them forever (/code-review smoke, Phase 1 round 1).
ADR_0036_GLOB = "KIT-ADR-0036*.md"

FEATURE_DEVELOPERS = [
    ".claude/agents/feature-developer.md",
    ".claude/agents/feature-developer-f5.md",
]
PLANNERS = [
    ".claude/agents/planner.md",
    ".claude/agents/planner-f5.md",
]
# The reviewer roster the read-only carve-out governs. architecture-reviewer
# is born in Phase 2; it joins the roster the moment the file exists.
REVIEWER_AGENTS = [
    ".claude/agents/code-reviewer.md",
    ".claude/agents/security-reviewer.md",
    ".claude/agents/document-reviewer.md",
    ".claude/agents/architecture-reviewer.md",
]

FLAG_FIELD = "**Review Flags**:"
FLAG_NAMES = ("architecture", "security", "docs-audit")


def _read(rel):
    return (REPO / rel).read_text(encoding="utf-8")


def _frontmatter(text):
    """The YAML frontmatter block between the leading --- fences.

    Tolerates a BOM and CRLF line endings (o3 evaluator, Phase 1
    round 1) so an editor's save style cannot red-bar the suite.
    """
    match = re.match("\\A\ufeff?---\\r?\\n(.*?)\\r?\\n---\\r?\\n", text, re.DOTALL)
    assert match, "no frontmatter block"
    return match.group(1)


def _declared_tools(frontmatter):
    """Tool names under the ``tools:`` key, lower-cased.

    Reads the whole value block up to the next top-level key, so both
    the bullet form (``- Read``) and an inline list (``tools: [Read]``)
    are seen, and case variants cannot slip a tool past the carve-out
    check (o3 evaluator, Phase 1 round 1).
    """
    match = re.search(r"^tools:(.*?)(?=^\S|\Z)", frontmatter, re.MULTILINE | re.DOTALL)
    if not match:
        return []
    return [t.lower() for t in re.findall(r"[A-Za-z_]\w*", match.group(1))]


# ---------------------------------------------------------------------------
# Phase 1 — the value authority


def test_review_pipeline_doc_is_the_value_authority():
    path = REPO / REVIEW_PIPELINE
    assert path.is_file(), f"{REVIEW_PIPELINE} missing — it is the single authority"
    text = _read(REVIEW_PIPELINE)
    # The authoritative flag registry lives here and nowhere else.
    for flag in FLAG_NAMES:
        assert re.search(rf"`{flag}`", text), (
            f"{REVIEW_PIPELINE}: flag registry must define `{flag}` "
            "(FR-7 — the spec's list is illustrative, this one is authoritative)"
        )
    # The binding tier-third-axis heuristic (spec Notes, planner 2026-08-24).
    assert "flag_presence_is_not_flag_emptiness" in text, (
        f"{REVIEW_PIPELINE}: the argv/input-validation axis must cite "
        "patterns.yml flag_presence_is_not_flag_emptiness (KIT-0118 evidence)"
    )
    assert re.search(r"bot-favourable\s+and\s+evaluator-hostile", text), (
        f"{REVIEW_PIPELINE}: must encode the third axis — argv/input-"
        "validation seams are bot-favourable and evaluator-hostile"
    )
    # The evidence contract preflight's Gate 8 checks.
    assert "-review-pass.md" in text, (
        f"{REVIEW_PIPELINE}: must define the review-pass record "
        "(.kit/context/reviews/<TASK-ID>-review-pass.md) — Gate 8's artifact"
    )
    # Tier 3 stays opt-in in the fd's own voice (FR-11).
    assert (
        "never self-escalates" in text
    ), f"{REVIEW_PIPELINE}: Tier 3 opt-in rule missing (FR-11)"


# ---------------------------------------------------------------------------
# Phase 1 — gate count on the instruction surfaces


@pytest.mark.parametrize("surface", [PREFLIGHT_CMD, COMMIT_PUSH_PR_CMD])
def test_no_stale_seven_gate_literals(surface):
    """The completion-gate count is 8 from Phase 1 on. The 7-gate literals
    that survive legitimately belong to the `agentive preflight` CLI
    (which keeps emitting mechanical gates 1-7 — Gate 8 is session-checked
    until mechanized); the *command surfaces* must not carry a stale 7."""
    text = _read(surface)
    # Also catches the verdict idiom ("all 7 pass") and the hyphenated
    # form ("7-gate") — the /code-review smoke found the original
    # pattern required the literal noun "gates" and would have missed a
    # regression of preflight's READY rule (Phase 1 round 1).
    stale = re.findall(
        r"(?:all\s+)?(?:7|seven)\s+(?:completion\s+)?gates\b"
        r"|\ball\s+7\s+pass\b|\b7-gate\b",
        text,
        re.I,
    )
    assert not stale, f"{surface}: stale 7-gate literal(s): {stale}"


def test_preflight_declares_gate_8():
    text = _read(PREFLIGHT_CMD)
    assert re.search(
        r"^\|\s*8\s*\|", text, re.MULTILINE
    ), f"{PREFLIGHT_CMD}: gate table has no row 8 (FR-3)"
    assert "REVIEW-PIPELINE.md" in text, (
        f"{PREFLIGHT_CMD}: Gate 8 must cite the review-pipeline authority, "
        "not restate its rules (KIT-0101 R5)"
    )
    assert "-review-pass.md" in text, (
        f"{PREFLIGHT_CMD}: Gate 8 must name its artifact "
        "(.kit/context/reviews/<TASK-ID>-review-pass.md)"
    )


# ---------------------------------------------------------------------------
# Phase 1 — fd gate sequence and docs habit


@pytest.mark.parametrize("agent", FEATURE_DEVELOPERS)
def test_fd_native_review_gate_between_evaluator_and_ship(agent):
    """FR-1/FR-2: /code-review runs after the evaluator gate, before Ship
    (pre-PR — same ordering rationale as KIT-0035), with /security-review
    in the same slot when the security flag is declared."""
    text = _read(agent)
    evaluator = text.find("## Phase 5: Evaluator")
    native = text.find("## Phase 5b: Native Review Pass")
    ship = text.find("## Phase 6: Ship")
    assert -1 not in (evaluator, native, ship), (
        f"{agent}: expected Phase 5 (Evaluator), Phase 5b (Native Review "
        "Pass) and Phase 6 (Ship) headings"
    )
    assert evaluator < native < ship, (
        f"{agent}: the native review pass must sit between the evaluator "
        "gate and Ship (pre-PR, FR-1)"
    )
    phase5b = text[native:ship]
    assert "/code-review" in phase5b, f"{agent}: Phase 5b must invoke /code-review"
    assert "/security-review" in phase5b, (
        f"{agent}: Phase 5b must run /security-review when the security "
        "flag is declared (FR-2)"
    )
    assert (
        "never silently skipped" in phase5b
    ), f"{agent}: flagged dimensions are never silently skipped (FR-2)"
    assert (
        "-review-pass.md" in phase5b
    ), f"{agent}: Phase 5b must persist the review-pass record (Gate 8)"
    assert (
        "REVIEW-PIPELINE.md" in phase5b
    ), f"{agent}: Phase 5b cites the value authority (KIT-0101 R5)"


@pytest.mark.parametrize("agent", FEATURE_DEVELOPERS)
def test_fd_docs_habit_before_preflight(agent):
    """FR-9: a standing update-the-docs step before preflight; the
    document-reviewer is a flagged periodic audit, not a per-task gate."""
    text = _read(agent)
    habit = text.find("update the docs your diff touches")
    preflight = text.find("## Phase 8: Preflight")
    assert habit != -1, f"{agent}: docs-habit step missing (FR-9)"
    assert preflight != -1, f"{agent}: Phase 8 (Preflight) heading missing"
    assert habit < preflight, f"{agent}: docs habit must precede preflight (FR-9)"


# ---------------------------------------------------------------------------
# Phase 1 — the flag field: planners declare, the template carries the shell


@pytest.mark.parametrize("agent", PLANNERS)
def test_planner_declares_review_flags_citing_authority(agent):
    text = _read(agent)
    assert FLAG_FIELD in text, (
        f"{agent}: planners set the optional {FLAG_FIELD} field at "
        "spec/handoff time (FR-7)"
    )
    assert "REVIEW-PIPELINE.md" in text, (
        f"{agent}: trigger heuristics live in REVIEW-PIPELINE.md — cite, "
        "never restate (FR-7, KIT-0101 R5)"
    )


def test_starter_template_carries_flag_shell_and_bumped_version():
    text = _read(STARTER_TEMPLATE)
    assert (
        FLAG_FIELD in text
    ), f"{STARTER_TEMPLATE}: must carry the Review Flags field shell (FR-7)"
    match = re.search(r"\*\*Version\*\*: (\d+)\.(\d+)\.(\d+)", text)
    assert match, f"{STARTER_TEMPLATE}: version line missing"
    assert tuple(int(g) for g in match.groups()) >= (2, 2, 0), (
        f"{STARTER_TEMPLATE}: adding the field shell bumps the template "
        "version to >= 2.2.0 (single starter authority contract)"
    )


# ---------------------------------------------------------------------------
# Phase 2 — armed mechanically by the ADR's existence


def _adr_0036():
    """The carve-out ADR's path, resolved by number (any slug), or None."""
    matches = sorted((REPO / ".kit" / "adr").glob(ADR_0036_GLOB))
    return matches[0] if matches else None


def _adr_exists():
    return _adr_0036() is not None


@pytest.mark.parametrize("agent", REVIEWER_AGENTS)
def test_reviewer_toolsets_satisfy_readonly_carveout(agent):
    """FR-6 / KIT-ADR-0036 §3: delegation-eligible iff EVERY declared
    tool is on the agent's ruled allow-list. Bash is rejected outright
    — no reviewer holds it, and re-ruling it means editing this test,
    the agent body, and the ADR's §3 table in one PR (heading/content
    checks against a not-yet-existing enumeration format proved
    vacuously satisfiable — evaluator + bot convergent, Phase 2)."""
    if not _adr_exists():
        pytest.skip("KIT-ADR-0036 not yet authored — arms in Phase 2")
    path = REPO / agent
    if not path.is_file():
        if agent.endswith("architecture-reviewer.md"):
            pytest.fail(
                "architecture-reviewer.md must exist once KIT-ADR-0036 "
                "lands (FR-8 — born read-only)"
            )
        pytest.skip(f"{agent} absent")
    text = path.read_text(encoding="utf-8")
    tools = set(_declared_tools(_frontmatter(text)))
    # KIT-ADR-0036 §3 is an IFF over an allow-list — "delegation-
    # eligible iff EVERY declared tool is on this ruled roster". A
    # deny-list inverts that shape: a reviewer declaring e.g. Task (the
    # very tool the ADR fences) would pass silently (architecture-
    # reviewer smoke finding, Phase 2 round 1). MCP tools (Serena) are
    # harness-inherited, never frontmatter-declared, so they don't
    # appear here — §3 rules them separately.
    allowed = {"read", "grep", "glob"} | {
        "code-reviewer.md": {"todowrite"},
        "security-reviewer.md": {"websearch"},
        "document-reviewer.md": {"websearch", "webfetch"},
        "architecture-reviewer.md": set(),
    }[agent.rsplit("/", 1)[-1]]
    unruled = tools - allowed
    assert not unruled, (
        f"{agent}: declares tool(s) {sorted(unruled)} not on its "
        "KIT-ADR-0036 §3 roster — rule each in the ADR (same PR) or "
        "remove them; the carve-out is iff-shaped. Bash in particular "
        "is rejected OUTRIGHT: as of KIT-ADR-0036 no reviewer holds "
        "it, and heading/content checks against a hypothetical "
        "enumeration format were vacuously satisfiable (evaluator + "
        "bot convergent, Phase 2). Re-ruling Bash means editing this "
        "test, the agent body, AND the ADR's §3 table in one PR — "
        "which is exactly the deliberate act the ADR requires."
    )


def test_every_reviewer_is_consumer_excluded():
    """Reviewer agents stay builder-only: each .claude/agents/
    *-reviewer.md must be rsync-excluded in BOTH engine-consumer.sh
    copies. Adding architecture-reviewer took six coordinated edits and
    the packaged-engine one was missed (architecture-reviewer smoke,
    Phase 2 round 1) — this converts the class into a red bar
    (patterns.yml two_homes_get_a_pin)."""
    reviewers = sorted(p.name for p in (REPO / ".claude/agents").glob("*-reviewer.md"))
    assert reviewers, "reviewer roster glob matched nothing"
    engines = [
        "scripts/local/engine-consumer.sh",
        "packages/agentive-kit/src/agentive_kit/door/engines/engine-consumer.sh",
    ]
    for engine in engines:
        text = _read(engine)
        for reviewer in reviewers:
            assert f"--exclude='{reviewer}'" in text, (
                f"{engine}: missing --exclude='{reviewer}' — a builder-only "
                "reviewer would ship into consumer scaffolds"
            )


@pytest.mark.parametrize(
    "agent",
    FEATURE_DEVELOPERS + PLANNERS + [".claude/agents/powertest-runner.md"],
)
def test_delegation_rules_cite_the_adr(agent):
    """FR-5: every body restating the no-delegation rule cites the
    carve-out ADR once it exists (footgun text updated to match).
    powertest-runner restates reviewer-delegation law too — it stated
    the OPPOSITE for three commits before the Tier-1 smoke caught it
    (Phase 2 round 1), so it joins the pinned roster."""
    if not _adr_exists():
        pytest.skip("KIT-ADR-0036 not yet authored — arms in Phase 2")
    assert "KIT-ADR-0036" in _read(
        agent
    ), f"{agent}: the delegation rule must cite KIT-ADR-0036 (FR-5)"
