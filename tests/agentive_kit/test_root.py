"""Tests for agentive_kit.root — CWD-walk project-root discovery.

KIT-0090 F2 calls this the highest-risk behavioral change of the
extraction: a globally installed CLI must resolve the project from the
current directory (never from its own install location) and refuse
loudly outside a kit repo — never operate on a guessed root.

Discovery rule under test: the nearest ancestor with BOTH a ``.kit/``
directory and a ``CLAUDE.md`` file. The kit-install marker region is
deliberately NOT required — the agentive-starter-kit repo itself must
be discoverable (F5 dogfood) and, being the upstream rather than a
bootstrapped consumer, carries no marker.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip(
    "agentive_kit", reason="agentive-kit package source present only in the kit repo"
)

from agentive_kit.root import RootNotFoundError, find_project_root  # noqa: E402


def make_kit_root(base: Path) -> Path:
    """Give ``base`` the two markers that make it a kit project root."""
    (base / ".kit").mkdir(parents=True, exist_ok=True)
    (base / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    return base


class TestDiscovery:
    def test_finds_root_from_root_itself(self, tmp_path):
        root = make_kit_root(tmp_path)
        assert find_project_root(root) == root

    def test_finds_root_from_nested_subdir(self, tmp_path):
        root = make_kit_root(tmp_path)
        nested = root / "scripts" / "core" / "doctor.d"
        nested.mkdir(parents=True)
        assert find_project_root(nested) == root

    def test_nearest_root_wins(self, tmp_path):
        outer = make_kit_root(tmp_path)
        inner = make_kit_root(outer / "vendor" / "other-project")
        start = inner / "docs"
        start.mkdir()
        assert find_project_root(start) == inner

    def test_planning_shape_repo_found(self, tmp_path):
        # A split-pair planning repo has .kit/ and CLAUDE.md but no
        # pyproject/tests/venv — discovery must not require any of those.
        root = make_kit_root(tmp_path)
        (root / ".kit" / "tasks" / "2-todo").mkdir(parents=True)
        assert find_project_root(root / ".kit" / "tasks") == root

    def test_worktree_checkout_found(self, tmp_path):
        # A linked worktree carries the full tree with .git as a FILE —
        # discovery reads only .kit/ + CLAUDE.md, so the worktree's own
        # root wins and the primary clone is never consulted.
        root = make_kit_root(tmp_path / "wt")
        (root / ".git").write_text(
            "gitdir: /elsewhere/.git/worktrees/wt\n", encoding="utf-8"
        )
        sub = root / "src"
        sub.mkdir()
        assert find_project_root(sub) == root

    def test_default_start_is_cwd(self, tmp_path, monkeypatch):
        root = make_kit_root(tmp_path)
        nested = root / "a" / "b"
        nested.mkdir(parents=True)
        monkeypatch.chdir(nested)
        assert find_project_root() == root

    def test_relative_start_path(self, tmp_path, monkeypatch):
        root = make_kit_root(tmp_path)
        nested = root / "a"
        nested.mkdir()
        monkeypatch.chdir(nested)
        assert find_project_root(Path(".")) == root


class TestRefusal:
    def test_refuses_outside_kit_repo(self, tmp_path):
        plain = tmp_path / "not-a-kit-project"
        plain.mkdir()
        with pytest.raises(RootNotFoundError) as exc_info:
            find_project_root(plain)
        message = str(exc_info.value)
        assert "Not inside an agentive project" in message
        assert str(plain) in message
        assert ".kit/ and CLAUDE.md" in message

    def test_claude_md_alone_not_enough(self, tmp_path):
        (tmp_path / "CLAUDE.md").write_text("# Docs\n", encoding="utf-8")
        with pytest.raises(RootNotFoundError):
            find_project_root(tmp_path)

    def test_kit_dir_alone_not_enough(self, tmp_path):
        (tmp_path / ".kit").mkdir()
        with pytest.raises(RootNotFoundError):
            find_project_root(tmp_path)

    def test_kit_as_file_not_enough(self, tmp_path):
        (tmp_path / ".kit").write_text("", encoding="utf-8")
        (tmp_path / "CLAUDE.md").write_text("# P\n", encoding="utf-8")
        with pytest.raises(RootNotFoundError):
            find_project_root(tmp_path)

    def test_claude_md_as_dir_not_enough(self, tmp_path):
        (tmp_path / ".kit").mkdir()
        (tmp_path / "CLAUDE.md").mkdir()
        with pytest.raises(RootNotFoundError):
            find_project_root(tmp_path)

    def test_partial_markers_do_not_stop_the_walk(self, tmp_path):
        # A child with only one marker must not shadow a real root above.
        root = make_kit_root(tmp_path)
        half = root / "docs"
        half.mkdir()
        (half / "CLAUDE.md").write_text("# Sub\n", encoding="utf-8")
        assert find_project_root(half) == root
