"""One canonical skills home (ADR-0027 P6, KIT-0057).

`.claude/skills/` is the single repo home for ALL skills — it is Claude
Code's own resolution path and the home the consumer engine distributes.
The `.kit/skills/<name>/SKILL.md` read-both symlinks that bridged one
release (the N1 deprecation cycle) were removed in 0.9.0 by KIT-0059,
alongside KIT-0047 and KIT-0054's pinned removals —
TestDeprecatedHomeRetired guards that the old home stays gone.
"""

from __future__ import annotations

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


class TestDeprecatedHomeRetired:
    def test_kit_skills_is_gone(self):
        """KIT-0059 (0.9.0): the read-both deprecation cycle is over —
        nothing may land in .kit/skills/ again; skills live only in
        .claude/skills/. is_symlink() is checked separately because
        exists() follows links and reports False for a dangling one
        (CodeRabbit, PR #100)."""
        assert not DEPRECATED.exists() and not DEPRECATED.is_symlink(), (
            f"{DEPRECATED} has reappeared — the skills home is "
            ".claude/skills/ only (KIT-0057/KIT-0059)"
        )
