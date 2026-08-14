"""Tests for scripts/local/plugin_resync.py — the release resync tool.

KIT-0110 R1: the tool derives its work-list from roster hashes (never
git diff), three-way-merges kit changes onto the published plugin bodies
(never copies over them), surfaces conflicts for the human, fails loud
when the merge base can't be recovered from kit history, and maintains
the roster's ``plugin_sha256`` column (the marketplace CI check's input).
All tests run against tmp fixture repos — no network.
"""

from __future__ import annotations

import hashlib
import importlib.util
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
_MODULE_PATH = REPO_ROOT / "scripts" / "local" / "plugin_resync.py"

# plugin_resync.py is kit-internal (scripts/local is not synced
# downstream — consumers have no plugin roster to resync). The consumer
# sync also excludes this test, but guard the load so a stray copy skips
# cleanly.
if not _MODULE_PATH.exists():
    pytest.skip(
        "plugin_resync.py present only in the kit repo",
        allow_module_level=True,
    )

_spec = importlib.util.spec_from_file_location("plugin_resync", _MODULE_PATH)
prs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(prs)


V1_BODY = """\
---
name: demo-agent
version: 1.0.0
---
# Demo agent

Shared intro line.

## Project Context

Kit-specific context the plugin generalizes away.

## Workflow

Step one.
"""

# v2 = kit moved on: a new workflow step at the bottom.
V2_BODY = V1_BODY + "\nStep two (added since the last release).\n"

# The published plugin body: derived from v1, with a legitimate
# KIT-ADR-0025 generalization in the middle (non-overlapping with the
# v1→v2 change).
PLUGIN_BODY = V1_BODY.replace(
    "Kit-specific context the plugin generalizes away.",
    "Generalized context for downstream consumers.",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=test",
            "-c",
            "user.email=test@example.invalid",
            *args,
        ],
        check=True,
        capture_output=True,
    )


@pytest.fixture
def kit(tmp_path):
    """A miniature kit git repo whose one agent has v1 → v2 history."""
    root = tmp_path / "kit"
    (root / ".claude" / "agents").mkdir(parents=True)
    _git(root, "init", "-q")
    agent = root / ".claude" / "agents" / "demo-agent.md"
    agent.write_text(V1_BODY, encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "v1")
    agent.write_text(V2_BODY, encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "v2")
    return root


@pytest.fixture
def marketplace(tmp_path):
    """A miniature marketplace checkout: roster + one published body."""
    root = tmp_path / "marketplace"
    plugin = root / "plugins" / "agentive-workflow"
    (plugin / "agents").mkdir(parents=True)
    (plugin / "agents" / "demo-agent.md").write_text(PLUGIN_BODY, encoding="utf-8")
    return root


def _write_roster(marketplace: Path, kit_sha256: str, extra: str = "") -> Path:
    roster = marketplace / "plugins" / "agentive-workflow" / "roster.yaml"
    roster.write_text(
        f"""\
# roster header comment — must survive updates
plugin: agentive-workflow
plugin_version: "2.0.4"
components:
  - name: demo-agent
    kind: agent
    ships: true
    source: .claude/agents/demo-agent.md
    kit_version: "0.9.0"
    kit_sha256: {kit_sha256}
    why: >-
      test agent
  - name: kit-side-only
    kind: agent
    ships: false
    source: .claude/agents/kit-side-only.md
    why: >-
      stays kit-side
{extra}""",
        encoding="utf-8",
    )
    return roster


def _run(kit: Path, marketplace: Path, *flags: str) -> int:
    return prs.main(
        [
            "--kit-root",
            str(kit),
            "--marketplace-root",
            str(marketplace),
            *flags,
        ]
    )


class TestWorkList:
    def test_in_sync_roster_yields_empty_worklist(self, kit, marketplace, capsys):
        _write_roster(marketplace, _sha(V2_BODY.encode()))
        assert _run(kit, marketplace, "--dry-run") == prs.EXIT_OK
        assert "work-list: empty" in capsys.readouterr().out

    def test_drift_detected_from_roster_hash_not_git_diff(
        self, kit, marketplace, capsys
    ):
        """The delta comes from the rostered hash (KIT-0099), so a stale
        roster flags drift even with a clean kit working tree."""
        _write_roster(marketplace, _sha(V1_BODY.encode()))
        assert _run(kit, marketplace, "--dry-run") == prs.EXIT_OK
        out = capsys.readouterr().out
        assert "1 drifted component(s)" in out
        assert "demo-agent" in out

    def test_dry_run_writes_nothing(self, kit, marketplace):
        roster = _write_roster(marketplace, _sha(V1_BODY.encode()))
        before_roster = roster.read_text(encoding="utf-8")
        body = marketplace / "plugins" / "agentive-workflow" / "agents"
        before_body = (body / "demo-agent.md").read_text(encoding="utf-8")
        _run(kit, marketplace, "--dry-run")
        assert roster.read_text(encoding="utf-8") == before_roster
        assert (body / "demo-agent.md").read_text(encoding="utf-8") == before_body


class TestThreeWayMerge:
    def test_clean_merge_preserves_generalization(self, kit, marketplace):
        """THE method (KIT-0109): kit v1→v2 change lands in the plugin
        body WITHOUT flattening the ADR-0025 generalization."""
        _write_roster(marketplace, _sha(V1_BODY.encode()))
        assert _run(kit, marketplace) == prs.EXIT_OK
        merged = (
            marketplace / "plugins" / "agentive-workflow" / "agents" / "demo-agent.md"
        ).read_text(encoding="utf-8")
        assert "Step two (added since the last release)." in merged
        assert "Generalized context for downstream consumers." in merged
        assert "Kit-specific context" not in merged

    def test_clean_merge_updates_roster_columns(self, kit, marketplace):
        roster = _write_roster(marketplace, _sha(V1_BODY.encode()))
        assert _run(kit, marketplace) == prs.EXIT_OK
        text = roster.read_text(encoding="utf-8")
        merged_body = (
            marketplace / "plugins" / "agentive-workflow" / "agents" / "demo-agent.md"
        ).read_bytes()
        assert f"kit_sha256: {_sha(V2_BODY.encode())}" in text
        assert f"plugin_sha256: {_sha(merged_body)}" in text
        # kit_version refreshed from the component's frontmatter
        assert 'kit_version: "1.0.0"' in text
        # header comment and kit-side entry survive the textual update
        assert text.startswith("# roster header comment")
        assert "kit-side-only" in text

    def test_kit_side_entries_untouched(self, kit, marketplace):
        roster = _write_roster(marketplace, _sha(V1_BODY.encode()))
        _run(kit, marketplace)
        text = roster.read_text(encoding="utf-8")
        # ships:false entries get no hash columns
        kit_side = text[text.index("- name: kit-side-only") :]
        assert "plugin_sha256" not in kit_side
        assert "kit_sha256" not in kit_side

    def test_conflict_surfaced_not_flattened(self, kit, marketplace, capsys):
        """THE falsification (spec AC): divergent plugin body + canon
        change on the same line → conflict surfaced, body untouched,
        roster hash NOT bumped."""
        agent = kit / ".claude" / "agents" / "demo-agent.md"
        conflicted = V2_BODY.replace(
            "Kit-specific context the plugin generalizes away.",
            "Kit-specific context, rewritten in canon.",
        )
        agent.write_text(conflicted, encoding="utf-8")
        _git(kit, "add", ".")
        _git(kit, "commit", "-q", "-m", "v3 touches the generalized line")
        roster = _write_roster(marketplace, _sha(V1_BODY.encode()))
        assert _run(kit, marketplace) == prs.EXIT_CONFLICTS
        out = capsys.readouterr().out
        assert "CONFLICT" in out
        body_dir = marketplace / "plugins" / "agentive-workflow" / "agents"
        # published body untouched
        assert (body_dir / "demo-agent.md").read_text(encoding="utf-8") == PLUGIN_BODY
        # conflict-marked merge written beside it for the human
        conflict_file = body_dir / "demo-agent.md.conflict"
        assert conflict_file.is_file()
        assert "<<<<<<<" in conflict_file.read_text(encoding="utf-8")
        # roster still records the OLD kit hash for the conflicted entry
        text = roster.read_text(encoding="utf-8")
        assert f"kit_sha256: {_sha(V1_BODY.encode())}" in text
        # but plugin_sha256 records the (unchanged) published body honestly
        assert f"plugin_sha256: {_sha(PLUGIN_BODY.encode())}" in text

    def test_new_component_without_body_is_copied(self, kit, marketplace):
        """A rostered ships:true component with no published body yet is
        copied (there is nothing to merge with) — loudly, not silently."""
        agent2 = kit / ".claude" / "agents" / "brand-new.md"
        agent2.write_text("---\nname: brand-new\n---\nnew body\n", encoding="utf-8")
        _git(kit, "add", ".")
        _git(kit, "commit", "-q", "-m", "add brand-new")
        extra = f"""\
  - name: brand-new
    kind: agent
    ships: true
    source: .claude/agents/brand-new.md
    kit_sha256: {"a" * 64}
    why: >-
      new component
"""
        _write_roster(marketplace, _sha(V2_BODY.encode()), extra=extra)
        assert _run(kit, marketplace) == prs.EXIT_OK
        copied = (
            marketplace / "plugins" / "agentive-workflow" / "agents" / "brand-new.md"
        )
        assert copied.read_text(encoding="utf-8").endswith("new body\n")


class TestBaseNotFound:
    def test_unmatchable_hash_fails_loud_and_writes_nothing(
        self, kit, marketplace, capsys
    ):
        """Spec AC: no historical version matches the rostered hash →
        loud per-component failure, never a silent copy."""
        roster = _write_roster(marketplace, "f" * 64)
        before_roster = roster.read_text(encoding="utf-8")
        body = (
            marketplace / "plugins" / "agentive-workflow" / "agents" / "demo-agent.md"
        )
        assert _run(kit, marketplace) == prs.EXIT_INTEGRITY
        out = capsys.readouterr().out
        assert "demo-agent" in out
        assert "Refusing" in out
        assert roster.read_text(encoding="utf-8") == before_roster
        assert body.read_text(encoding="utf-8") == PLUGIN_BODY

    def test_missing_body_on_undrifted_component_aborts_before_writes(
        self, kit, marketplace, capsys
    ):
        """Bot round 1 (convergent BugBot + CodeRabbit): a non-drifted
        shipped component with no published body must abort in preflight —
        BEFORE the merge loop writes anything — never leave merged bodies
        on disk with the roster unwritten."""
        agent2 = kit / ".claude" / "agents" / "settled.md"
        agent2.write_text("---\nname: settled\n---\nsettled body\n", encoding="utf-8")
        _git(kit, "add", ".")
        _git(kit, "commit", "-q", "-m", "add settled")
        extra = f"""\
  - name: settled
    kind: agent
    ships: true
    source: .claude/agents/settled.md
    kit_sha256: {_sha(agent2.read_bytes())}
    why: >-
      in-sync component whose body was never copied
"""
        # demo-agent IS drifted, so the merge loop would write its body —
        # the preflight must fire first and write nothing at all.
        roster = _write_roster(marketplace, _sha(V1_BODY.encode()), extra=extra)
        before_roster = roster.read_text(encoding="utf-8")
        body = (
            marketplace / "plugins" / "agentive-workflow" / "agents" / "demo-agent.md"
        )
        assert _run(kit, marketplace) == prs.EXIT_INTEGRITY
        out = capsys.readouterr().out
        assert "settled" in out
        assert "nothing written" in out
        assert roster.read_text(encoding="utf-8") == before_roster
        assert body.read_text(encoding="utf-8") == PLUGIN_BODY

    def test_missing_kit_source_fails_loud(self, kit, marketplace, capsys):
        _write_roster(marketplace, _sha(V1_BODY.encode()))
        (kit / ".claude" / "agents" / "demo-agent.md").unlink()
        assert _run(kit, marketplace) == prs.EXIT_INTEGRITY
        assert "missing from the kit" in capsys.readouterr().out


class TestHashesOnly:
    def test_column_populated_without_touching_bodies(self, kit, marketplace):
        """R2's input: --hashes-only writes plugin_sha256 for every
        shipped component and leaves drifted bodies alone."""
        roster = _write_roster(marketplace, _sha(V1_BODY.encode()))
        assert _run(kit, marketplace, "--hashes-only") == prs.EXIT_OK
        text = roster.read_text(encoding="utf-8")
        assert f"plugin_sha256: {_sha(PLUGIN_BODY.encode())}" in text
        # drifted kit hash deliberately untouched in this mode
        assert f"kit_sha256: {_sha(V1_BODY.encode())}" in text
        body = (
            marketplace / "plugins" / "agentive-workflow" / "agents" / "demo-agent.md"
        )
        assert body.read_text(encoding="utf-8") == PLUGIN_BODY

    def test_existing_column_is_replaced_not_duplicated(self, kit, marketplace):
        roster = _write_roster(marketplace, _sha(V2_BODY.encode()))
        _run(kit, marketplace, "--hashes-only")
        _run(kit, marketplace, "--hashes-only")
        text = roster.read_text(encoding="utf-8")
        assert text.count("plugin_sha256:") == 1

    def test_missing_body_fails_loud(self, kit, marketplace, capsys):
        _write_roster(marketplace, _sha(V2_BODY.encode()))
        (
            marketplace / "plugins" / "agentive-workflow" / "agents" / "demo-agent.md"
        ).unlink()
        assert _run(kit, marketplace, "--hashes-only") == prs.EXIT_INTEGRITY
        assert "run a full resync" in capsys.readouterr().out


class TestRosterValidation:
    def test_malformed_roster_takes_guard_exit(self, kit, marketplace):
        """Schema validation is the guard's own parser (evaluator F3) —
        the two tools cannot disagree about what a valid roster is."""
        roster = marketplace / "plugins" / "agentive-workflow" / "roster.yaml"
        roster.write_text("components: [null]\n", encoding="utf-8")
        with pytest.raises(SystemExit) as exc:
            _run(kit, marketplace)
        assert exc.value.code == prs.EXIT_ROSTER_IO

    def test_unknown_kind_rejected(self, kit, marketplace):
        extra = """\
  - name: oddity
    kind: gizmo
    ships: true
    source: .claude/agents/demo-agent.md
    kit_sha256: deadbeef
    why: >-
      unknown kind
"""
        _write_roster(marketplace, _sha(V2_BODY.encode()), extra=extra)
        with pytest.raises(SystemExit) as exc:
            _run(kit, marketplace)
        assert exc.value.code == prs.EXIT_ROSTER_IO

    def test_traversal_name_rejected(self, kit, marketplace):
        """Component names become body paths — a traversal name must die
        in validation, never reach the filesystem."""
        extra = f"""\
  - name: ../../escape
    kind: agent
    ships: true
    source: .claude/agents/demo-agent.md
    kit_sha256: {_sha(V2_BODY.encode())}
    why: >-
      escape attempt
"""
        _write_roster(marketplace, _sha(V2_BODY.encode()), extra=extra)
        with pytest.raises(SystemExit) as exc:
            _run(kit, marketplace)
        assert exc.value.code == prs.EXIT_ROSTER_IO

    def test_missing_roster_is_usage_error(self, kit, tmp_path):
        empty = tmp_path / "empty-marketplace"
        empty.mkdir()
        assert _run(kit, empty) == prs.EXIT_USAGE

    def test_non_git_kit_root_is_usage_error(self, tmp_path, marketplace):
        bare = tmp_path / "bare-kit"
        (bare / ".claude").mkdir(parents=True)
        _write_roster(marketplace, "0" * 64)
        assert _run(bare, marketplace) == prs.EXIT_USAGE


class TestHelpers:
    def test_frontmatter_version_extracted(self):
        assert prs.frontmatter_version(V1_BODY) == "1.0.0"

    def test_frontmatter_version_absent(self):
        assert prs.frontmatter_version("no frontmatter\n") is None
        assert prs.frontmatter_version("---\nname: x\n---\nbody\n") is None

    def test_entry_bounds_exact_name_match(self):
        """`demo` must never claim `demo-f5`'s block (== on the
        indent-anchored line, not startswith)."""
        lines = [
            "components:",
            "  - name: demo",
            "    kind: agent",
            "  - name: demo-f5",
            "    kind: agent",
        ]
        start, end = prs._entry_bounds(lines, "demo")
        assert (start, end) == (1, 3)
        start, end = prs._entry_bounds(lines, "demo-f5")
        assert (start, end) == (3, 5)

    def test_entry_bounds_ignores_lookalike_in_why_text(self):
        """A `why: >-` continuation line beginning `- name:` (indented
        deeper than the list) must neither open nor close an entry."""
        lines = [
            "components:",
            "  - name: demo",
            "    kind: agent",
            "    why: >-",
            "      - name: demo is mentioned here in prose",
            "  - name: next",
            "    kind: agent",
        ]
        start, end = prs._entry_bounds(lines, "demo")
        assert (start, end) == (1, 5)

    def test_skill_body_path(self):
        comp = {"name": "self-review", "kind": "skill"}
        assert prs.plugin_body_relpath(comp) == "skills/self-review/SKILL.md"
