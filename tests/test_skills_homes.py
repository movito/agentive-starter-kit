"""One canonical skills home (ADR-0027 P6, KIT-0057).

`.claude/skills/` is the single repo home for ALL skills — it is Claude
Code's own resolution path and the home the consumer engine distributes.
`.kit/skills/<name>/SKILL.md` survives ONE release as a relative
symlink into the canonical home, inside a REAL directory (the read-both
deprecation cycle, N1: agents and docs reading the old path keep
working — see the file-vs-dir symlink rationale in
TestReadBothDeprecationCycle). The links — and the
TestReadBothDeprecationCycle class below — are removed in 0.9.0 by
KIT-0059, alongside KIT-0047 and KIT-0054's pinned removals.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL = REPO_ROOT / ".claude" / "skills"
DEPRECATED = REPO_ROOT / ".kit" / "skills"

BUILDER_SKILLS = ("code-review-evaluator", "review-handoff", "self-review")
IMPLEMENTATION_SKILLS = ("bot-triage", "pre-implementation")
ALL_SKILLS = BUILDER_SKILLS + IMPLEMENTATION_SKILLS


class TestCanonicalHome:
    @pytest.mark.parametrize("skill", ALL_SKILLS)
    def test_skill_lives_in_claude_skills(self, skill):
        skill_dir = CANONICAL / skill
        skill_file = skill_dir / "SKILL.md"
        assert skill_file.is_file(), f"{skill} missing from the canonical home"
        assert not skill_dir.is_symlink(), (
            f"{skill_dir} must be a real directory — the canonical home "
            "holds content, never links"
        )
        text = skill_file.read_text(encoding="utf-8")
        assert text.startswith("---\n"), f"{skill}: SKILL.md needs frontmatter"
        assert (
            "description:" in text.split("---")[1]
        ), f"{skill}: frontmatter needs a description for skill resolution"

    def test_no_new_content_in_deprecated_home(self):
        """During the deprecation cycle the old home may hold ONLY the
        read-both link structure — real content there is a skill
        landing in the wrong home."""
        if not DEPRECATED.exists():
            pytest.skip(".kit/skills absent (consumer checkout)")
        for entry in DEPRECATED.iterdir():
            assert entry.name in BUILDER_SKILLS, (
                f"{entry} is new content in the deprecated home — "
                "new skills belong in .claude/skills/"
            )
            for child in entry.iterdir():
                assert child.is_symlink(), (
                    f"{child} is a real file in the deprecated home — "
                    "content lives only in .claude/skills/"
                )


@pytest.mark.skipif(
    not DEPRECATED.exists(), reason=".kit/skills absent (consumer checkout)"
)
class TestReadBothDeprecationCycle:
    """Read-both, tested from BOTH paths. Delete this class with the
    symlinks in 0.9.0 (KIT-0059)."""

    @pytest.mark.parametrize("skill", BUILDER_SKILLS)
    def test_old_path_still_reads_same_content(self, skill):
        old = DEPRECATED / skill / "SKILL.md"
        new = CANONICAL / skill / "SKILL.md"
        assert old.is_file(), f"read-both broken: {old} unreadable"
        assert old.read_text(encoding="utf-8") == new.read_text(encoding="utf-8")

    @pytest.mark.parametrize("skill", BUILDER_SKILLS)
    def test_old_path_is_relative_file_symlink_into_canonical_home(self, skill):
        """FILE-level symlinks inside real directories, deliberately:
        the manifest sync engine's _read_dir (rglob + is_file) does not
        descend into symlinked DIRECTORIES, so a dir-symlink would make
        a kit_builder pull-sync see .kit/skills/ as empty and prune
        consumer copies. A file symlink is followed by is_file() and
        ships as dereferenced content."""
        skill_dir = DEPRECATED / skill
        assert skill_dir.is_dir() and not skill_dir.is_symlink(), (
            f"{skill_dir} must be a real directory (sync engines do not "
            "descend into symlinked dirs)"
        )
        link = skill_dir / "SKILL.md"
        assert link.is_symlink(), f"{link} must be a symlink during the cycle"
        target = os.readlink(link)
        assert not os.path.isabs(target), (
            f"{link} -> {target}: must be relative (absolute links break "
            "on clone/export)"
        )
        assert (link.parent / target).resolve() == (
            CANONICAL / skill / "SKILL.md"
        ).resolve()

    def test_sync_engine_reads_content_through_old_path(self):
        """The seam this shape exists for: the pull-sync reader must see
        the three skills as real content under the deprecated entry."""
        sys.path.insert(0, str(REPO_ROOT / "scripts" / "core"))
        try:
            from sync_from_manifest import _read_dir
        finally:
            sys.path.pop(0)
        contents = _read_dir(DEPRECATED)
        assert set(contents) == {f"{s}/SKILL.md" for s in BUILDER_SKILLS}
        for skill in BUILDER_SKILLS:
            canonical = (CANONICAL / skill / "SKILL.md").read_bytes()
            assert contents[f"{skill}/SKILL.md"].data == canonical
