"""Tests for scripts/local/check_plugin_drift.py — the plugin drift guard.

KIT-0096 F4: the guard must FAIL when kit ``.claude/`` content is newer
than the last published plugin release (falsification is a spec acceptance
criterion), pass when in sync, and catch unrostered components. All tests
run against tmp fixtures — no network.
"""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
_MODULE_PATH = REPO_ROOT / "scripts" / "local" / "check_plugin_drift.py"

# check_plugin_drift.py is kit-internal (scripts/local is not synced
# downstream — consumer .claude/ trees come from the plugin, so the
# comparison is meaningless there). The consumer sync also excludes this
# test, but guard the load so a stray copy skips cleanly.
if not _MODULE_PATH.exists():
    pytest.skip(
        "check_plugin_drift.py present only in the kit repo",
        allow_module_level=True,
    )

_spec = importlib.util.spec_from_file_location("check_plugin_drift", _MODULE_PATH)
cpd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cpd)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def kit(tmp_path):
    """A miniature kit root with two agents, one command, one skill."""
    root = tmp_path / "kit"
    (root / ".claude" / "agents").mkdir(parents=True)
    (root / ".claude" / "commands").mkdir(parents=True)
    (root / ".claude" / "skills" / "self-review").mkdir(parents=True)
    (root / ".claude" / "agents" / "feature-developer.md").write_text(
        "---\nname: feature-developer\nversion: 2.1.1\n---\nbody\n",
        encoding="utf-8",
    )
    (root / ".claude" / "agents" / "bootstrap.md").write_text(
        "---\nname: bootstrap\n---\nkit-side body\n", encoding="utf-8"
    )
    (root / ".claude" / "commands" / "preflight.md").write_text(
        "---\ndescription: gates\n---\ncmd\n", encoding="utf-8"
    )
    (root / ".claude" / "skills" / "self-review" / "SKILL.md").write_text(
        "---\ndescription: audit\n---\nskill\n", encoding="utf-8"
    )
    return root


def _roster_for(root: Path) -> str:
    """A roster that matches the fixture kit exactly (in-sync state)."""
    fd = root / ".claude" / "agents" / "feature-developer.md"
    pf = root / ".claude" / "commands" / "preflight.md"
    sr = root / ".claude" / "skills" / "self-review" / "SKILL.md"
    return f"""\
plugin: agentive-workflow
plugin_version: "2.0.0"
components:
  - name: feature-developer
    kind: agent
    ships: true
    source: .claude/agents/feature-developer.md
    kit_sha256: {_sha(fd)}
    why: core agent
  - name: bootstrap
    kind: agent
    ships: false
    source: .claude/agents/bootstrap.md
    why: kit-side door interviewer
  - name: preflight
    kind: command
    ships: true
    source: .claude/commands/preflight.md
    kit_sha256: {_sha(pf)}
    why: workflow command
  - name: self-review
    kind: skill
    ships: true
    source: .claude/skills/self-review/SKILL.md
    kit_sha256: {_sha(sr)}
    why: workflow skill
"""


def _run(kit_root: Path, roster_text: str, tmp_path: Path) -> int:
    roster = tmp_path / "roster.yaml"
    roster.write_text(roster_text, encoding="utf-8")
    return cpd.main(["--roster-file", str(roster), "--kit-root", str(kit_root)])


class TestInSync:
    def test_matching_tree_passes(self, kit, tmp_path, capsys):
        assert _run(kit, _roster_for(kit), tmp_path) == cpd.EXIT_IN_SYNC
        assert "in sync" in capsys.readouterr().out

    def test_kit_side_entries_need_no_hash(self, kit, tmp_path):
        # bootstrap ships:false and carries no kit_sha256 — not a finding
        assert _run(kit, _roster_for(kit), tmp_path) == cpd.EXIT_IN_SYNC


class TestDrift:
    def test_kit_newer_than_release_fails(self, kit, tmp_path, capsys):
        """THE falsification scenario (spec AC): edit kit content -> FAIL."""
        roster = _roster_for(kit)  # hashes taken before the edit
        fd = kit / ".claude" / "agents" / "feature-developer.md"
        fd.write_text(
            fd.read_text(encoding="utf-8") + "\nnew contract\n", encoding="utf-8"
        )
        assert _run(kit, roster, tmp_path) == cpd.EXIT_DRIFT
        out = capsys.readouterr().out
        assert "newer than the published release" in out
        assert "feature-developer" in out

    def test_kit_side_edit_does_not_fail(self, kit, tmp_path):
        """Editing a ships:false component is not drift — consumers never
        see it."""
        roster = _roster_for(kit)
        bs = kit / ".claude" / "agents" / "bootstrap.md"
        bs.write_text(bs.read_text(encoding="utf-8") + "\nmore\n", encoding="utf-8")
        assert _run(kit, roster, tmp_path) == cpd.EXIT_IN_SYNC

    def test_deleted_source_fails(self, kit, tmp_path, capsys):
        roster = _roster_for(kit)
        (kit / ".claude" / "commands" / "preflight.md").unlink()
        assert _run(kit, roster, tmp_path) == cpd.EXIT_DRIFT
        assert "missing from the kit" in capsys.readouterr().out

    def test_unrostered_component_fails(self, kit, tmp_path, capsys):
        """A new .claude component with no roster entry violates the
        function-enumeration law (KIT-0067) -> FAIL."""
        roster = _roster_for(kit)
        (kit / ".claude" / "agents" / "brand-new.md").write_text(
            "---\nname: brand-new\n---\nbody\n", encoding="utf-8"
        )
        assert _run(kit, roster, tmp_path) == cpd.EXIT_DRIFT
        assert "unrostered component" in capsys.readouterr().out

    def test_source_escaping_kit_root_fails(self, kit, tmp_path, capsys):
        """Roster is remote input — a traversal source must be refused,
        never hashed (evaluator round 1, accepted)."""
        outside = tmp_path / "outside.md"
        outside.write_text("secret\n", encoding="utf-8")
        roster = _roster_for(kit) + f"""\
  - name: sneaky
    kind: agent
    ships: true
    source: ../outside.md
    kit_sha256: {_sha(outside)}
    why: escape attempt
"""
        assert _run(kit, roster, tmp_path) == cpd.EXIT_DRIFT
        assert "escapes the kit root" in capsys.readouterr().out

    def test_absolute_source_fails(self, kit, tmp_path, capsys):
        roster = _roster_for(kit) + """\
  - name: absolute
    kind: agent
    ships: true
    source: /etc/hosts
    kit_sha256: deadbeef
    why: escape attempt
"""
        assert _run(kit, roster, tmp_path) == cpd.EXIT_DRIFT
        assert "escapes the kit root" in capsys.readouterr().out

    def test_duplicate_source_fails(self, kit, tmp_path, capsys):
        roster = _roster_for(kit)
        dup = roster[roster.index("  - name: preflight") :]
        assert _run(kit, roster + dup, tmp_path) == cpd.EXIT_DRIFT
        assert "duplicate roster entry" in capsys.readouterr().out

    def test_shipped_entry_without_hash_fails(self, kit, tmp_path, capsys):
        roster = _roster_for(kit).replace(
            f"    kit_sha256: {_sha(kit / '.claude' / 'commands' / 'preflight.md')}\n",
            "",
        )
        assert _run(kit, roster, tmp_path) == cpd.EXIT_DRIFT
        assert "no kit_sha256" in capsys.readouterr().out


class TestErrors:
    def test_invalid_yaml_exits_roster_io(self, kit, tmp_path):
        roster = tmp_path / "roster.yaml"
        roster.write_text("components: [unclosed\n", encoding="utf-8")
        with pytest.raises(SystemExit) as exc:
            cpd.main(["--roster-file", str(roster), "--kit-root", str(kit)])
        assert exc.value.code == cpd.EXIT_ROSTER_IO

    def test_missing_components_key_exits_roster_io(self, kit, tmp_path):
        roster = tmp_path / "roster.yaml"
        roster.write_text("plugin: agentive-workflow\n", encoding="utf-8")
        with pytest.raises(SystemExit) as exc:
            cpd.main(["--roster-file", str(roster), "--kit-root", str(kit)])
        assert exc.value.code == cpd.EXIT_ROSTER_IO

    def test_unreadable_roster_file_exits_roster_io(self, kit, tmp_path):
        with pytest.raises(SystemExit) as exc:
            cpd.main(
                ["--roster-file", str(tmp_path / "absent.yaml"), "--kit-root", str(kit)]
            )
        assert exc.value.code == cpd.EXIT_ROSTER_IO

    def test_bad_kit_root_exits_usage(self, tmp_path):
        roster = tmp_path / "roster.yaml"
        roster.write_text("components: []\n", encoding="utf-8")
        code = cpd.main(["--roster-file", str(roster), "--kit-root", str(tmp_path)])
        assert code == cpd.EXIT_USAGE
