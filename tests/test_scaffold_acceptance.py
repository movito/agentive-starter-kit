"""Scaffold acceptance test — the door's output must demonstrably work.

KIT-0093 F5 (absorbing KIT-0082): a fresh ``bootstrap --new`` run per
shape is exercised end-to-end and its output asserted USABLE — not
merely that the install steps ran. Two assertion tiers:

- ``TestScaffoldInvariants``: must hold in BOTH the copying world
  (today) and the packaged world (after the KIT-0093 PR 2 door
  switch). These run plain.
- ``TestPackagedWorld``: the ADR-0028 phase 2 contract — no copied
  scripts/agents, verify-or-instruct lines for the two package
  installs. RED against today's door by design (the red-first
  falsifiability rule: a test born green against the old world proves
  nothing). Marked ``xfail(strict=True)`` so CI stays green while the
  door still copies, and the suite FAILS the moment the door changes
  without these markers being consciously removed — PR 2 removes them.

Shape-divergent findings (KIT-0081 F2/F8: the planning scaffold ships
no agent-handoffs.json and no README) carry the xfail marker only on
the shape where they are red today; the dangling-reference check is
red on both shapes (the single export's agent copies reference kit
ADRs the export deletes).

Contract strings the PR 2 door must print (defined HERE first, the
test being the contract's origin):
- lifecycle CLI verified:    a line starting ``agentive CLI:``
- lifecycle CLI absent:      ``Install the lifecycle CLI: uv tool install agentive-kit``
- agent plugin verified:     ``agent plugin: verified``
- agent plugin absent:       a line starting ``Install the agent plugin:``
Absence of a package is always an instruction, never a hard failure
(the KIT-0083 degradation pattern).

Consumer-rsync boundary: this module reads scripts/local/ content, so
it is excluded from the consumer tests/ rsync in engine-consumer.sh
(exclude + rm -f sweep) and module-skips when the door is absent.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# Explicit door check BEFORE the test_setup_door import (BugBot, this
# PR): the docstring's module-skip promise must not depend on the
# imported module's own guard surviving a partial scaffold.
_DOOR = Path(__file__).resolve().parent.parent / "scripts" / "local" / "bootstrap"
if not _DOOR.exists():
    pytest.skip(
        "setup door present only in the kit repo",
        allow_module_level=True,
    )

from test_setup_door import (  # noqa: E402
    _assert_env_invariants,
    _env_lines,
    _git_identity,
    _scrubbed_env,
    run_door,
)

# The one marker PR 2 removes: strict, so an accidentally-flipped door
# (or a green-by-construction assertion) fails the suite instead of
# silently draining the test of meaning.
RED_UNTIL_DOOR_SWITCH = pytest.mark.xfail(
    reason="RED until KIT-0093 PR 2 switches the door to package-install mode",
    strict=True,
)

BOTH_SHAPES_RED = pytest.mark.parametrize(
    "shape",
    [
        pytest.param("single", marks=RED_UNTIL_DOOR_SWITCH),
        pytest.param("planning", marks=RED_UNTIL_DOOR_SWITCH),
    ],
)

BOTH_SHAPES = pytest.mark.parametrize("shape", ["single", "planning"])

# KIT-0081 findings red on the planning shape only (single's git-archive
# export happens to ship the referenced files / README today).
PLANNING_RED = pytest.mark.parametrize(
    "shape",
    [
        pytest.param("single"),
        pytest.param("planning", marks=RED_UNTIL_DOOR_SWITCH),
    ],
)


@pytest.fixture(scope="module")
def single_scaffold(tmp_path_factory):
    base = tmp_path_factory.mktemp("accept-single")
    env = _scrubbed_env(XDG_CONFIG_HOME=str(_git_identity(base)))
    target = base / "fresh-single"
    result = run_door("--new", str(target), env=env)
    return target, result, env


@pytest.fixture(scope="module")
def planning_scaffold(tmp_path_factory):
    base = tmp_path_factory.mktemp("accept-planning")
    env = _scrubbed_env(XDG_CONFIG_HOME=str(_git_identity(base)))
    target = base / "fresh-planning"
    result = run_door(
        "--new",
        str(target),
        "--shape",
        "planning",
        "--target-path",
        "../product",
        env=env,
    )
    return target, result, env


def _scaffold(request, shape):
    return request.getfixturevalue(f"{shape}_scaffold")


_REF_PATTERN = re.compile(
    r"`((?:docs|\.kit)/[A-Za-z0-9_./-]+\.(?:md|json|ya?ml|sh|py))`"
)


def _is_placeholder(ref: str) -> bool:
    """Example paths (`ASK-XXXX-review.md`) are illustrations, not
    references — a dangling one is not a defect."""
    return "XXXX" in ref or "NNNN" in ref


def _referenced_paths(target: Path) -> dict[str, list[str]]:
    """Backtick-quoted docs/… and .kit/… file references per seeded
    guidance surface (CLAUDE.md + any agent copies) — the grep-and-test
    loop from the 2026-08-04 audit (KIT-0081 F2), automated."""
    surfaces = [target / "CLAUDE.md"]
    agents_dir = target / ".claude" / "agents"
    if agents_dir.is_dir():
        surfaces.extend(sorted(agents_dir.glob("*.md")))
    missing: dict[str, list[str]] = {}
    for surface in surfaces:
        text = surface.read_text(encoding="utf-8")
        dangling = [
            ref
            for ref in _REF_PATTERN.findall(text)
            if not _is_placeholder(ref) and not (target / ref).exists()
        ]
        if dangling:
            missing[str(surface.relative_to(target))] = sorted(set(dangling))
    return missing


@pytest.mark.slow
class TestScaffoldInvariants:
    """Hold in both worlds: the scaffold is usable on day one."""

    @BOTH_SHAPES
    def test_install_succeeds_and_reports(self, request, shape):
        target, result, env = _scaffold(request, shape)
        assert result.returncode == 0, result.stderr + result.stdout
        assert "Install complete:" in result.stdout

    @BOTH_SHAPES
    def test_env_invariants(self, request, shape):
        """KIT-0084: present, 0600, gitignored, identity filled —
        the TestEnvSeedingE2E assertions, applied to the acceptance
        scaffold."""
        target, result, env = _scaffold(request, shape)
        _assert_env_invariants(target, env)
        lines = _env_lines(target)
        assert f"PROJECT_NAME={target.name}" in lines
        prefix_lines = [ln for ln in lines if ln.startswith("TASK_PREFIX=")]
        assert prefix_lines, "TASK_PREFIX line must exist"
        assert prefix_lines[0] != "TASK_PREFIX=TASK", "never the old placeholder"
        if shape == "single":
            assert prefix_lines[0] != "TASK_PREFIX=", "single shape derives a prefix"

    @BOTH_SHAPES
    def test_kit_skeleton_present(self, request, shape):
        """The planner's Phase 1 triage paths exist."""
        target, result, env = _scaffold(request, shape)
        for d in (
            "1-backlog",
            "2-todo",
            "3-in-progress",
            "4-in-review",
            "5-done",
        ):
            assert (target / ".kit" / "tasks" / d).is_dir(), f"missing tasks/{d}"
        assert (target / ".kit" / "context").is_dir()

    @BOTH_SHAPES
    def test_entry_flow_reachable(self, request, shape):
        """A cold-open session is told what to do first (KIT-0067 F3),
        and the install record exists for every downstream reader."""
        target, result, env = _scaffold(request, shape)
        text = (target / "CLAUDE.md").read_text(encoding="utf-8")
        assert "BEGIN KIT-LOCAL: kit-install" in text
        assert "BEGIN KIT-LOCAL: first-session" in text

    @BOTH_SHAPES
    def test_doctor_ran_or_cli_instructed(self, request, shape):
        """Green-or-actionably-instructive, never silent: either doctor
        ran in the target, or the door printed the CLI install line."""
        target, result, env = _scaffold(request, shape)
        out = result.stdout
        assert (
            "Doctor verdict:" in out
            or "Install the lifecycle CLI: uv tool install agentive-kit" in out
        ), "door must run doctor or instruct installing the CLI"

    @BOTH_SHAPES
    def test_evaluator_path_pass_or_instructive(self, request, shape):
        """The evaluator provisioning line: PASS, or an instruction the
        operator can follow — never an unexplained failure (#103 trap)."""
        target, result, env = _scaffold(request, shape)
        lines = [ln for ln in result.stdout.splitlines() if "evaluator" in ln.lower()]
        assert lines, "door output must mention the evaluator path"
        # line-scoped, never whole-output: "Install complete:" would
        # otherwise satisfy the instruction arm vacuously
        assert any(
            "pass" in ln.lower() or "install" in ln.lower() for ln in lines
        ), f"no evaluator line passes or instructs: {lines}"

    @PLANNING_RED
    def test_readme_names_the_repo_purpose(self, request, shape):
        """KIT-0081 F8: a scaffold whose only Finder-visible contents
        are dot-folders reads as empty — a README must say what the
        repo is."""
        target, result, env = _scaffold(request, shape)
        readme = target / "README.md"
        assert readme.is_file(), "scaffold must ship a README.md"
        assert readme.read_text(encoding="utf-8").strip(), "README must not be empty"

    @PLANNING_RED
    def test_agent_handoffs_exists_for_planner_triage(self, request, shape):
        """KIT-0081 F2: the planner reads agent-handoffs.json from
        Phase 1 on; a scaffold without it dead-ends the first session."""
        target, result, env = _scaffold(request, shape)
        assert (target / ".kit" / "context" / "agent-handoffs.json").is_file()

    @BOTH_SHAPES_RED
    def test_zero_dangling_references(self, request, shape):
        """KIT-0081 F2: every docs/… and .kit/… file a seeded guidance
        surface references must exist in the scaffold. Red on BOTH
        shapes today (the single export's agent copies reference kit
        ADRs the export deletes — KIT-ADR-0014/0019). Trivial by
        construction once nothing is copied — asserted anyway."""
        target, result, env = _scaffold(request, shape)
        missing = _referenced_paths(target)
        assert not missing, f"dangling references in scaffold: {missing}"


@pytest.mark.slow
class TestPackagedWorld:
    """The ADR-0028 phase 2 contract — RED until the door switch."""

    @BOTH_SHAPES_RED
    def test_no_copied_core_scripts(self, request, shape):
        """agentive-kit provides the lifecycle scripts; the scaffold
        carries none."""
        target, result, env = _scaffold(request, shape)
        assert not (target / "scripts" / "core").exists(), (
            "scripts/core must not be copied — the agentive-kit package "
            "provides the lifecycle surface"
        )

    @BOTH_SHAPES_RED
    def test_no_copied_agent_bodies(self, request, shape):
        """The plugin provides agents/skills/commands; the scaffold
        carries no copies (project specifics live in repo-owned files
        per KIT-ADR-0025)."""
        target, result, env = _scaffold(request, shape)
        copied = [
            str(p.relative_to(target))
            for sub in ("agents", "skills", "commands")
            for p in (target / ".claude" / sub).rglob("*.md")
            if (target / ".claude" / sub).is_dir()
        ]
        assert not copied, f"agent/skill/command copies shipped: {copied}"

    @BOTH_SHAPES_RED
    def test_lifecycle_cli_verified_or_instructed(self, request, shape):
        """The door verifies `agentive` on PATH or prints the install
        line — the degradation pattern, never a hard fail."""
        target, result, env = _scaffold(request, shape)
        out = result.stdout
        assert (
            "agentive CLI:" in out
            or "Install the lifecycle CLI: uv tool install agentive-kit" in out
        ), "door must verify the agentive CLI or instruct installing it"

    @BOTH_SHAPES_RED
    def test_agent_plugin_verified_or_instructed(self, request, shape):
        """The door verifies the agentive-workflow plugin (the
        50-plugin-source.sh detection approach) or prints the install
        instruction."""
        target, result, env = _scaffold(request, shape)
        out = result.stdout
        assert (
            "agent plugin: verified" in out or "Install the agent plugin:" in out
        ), "door must verify the plugin or instruct installing it"
