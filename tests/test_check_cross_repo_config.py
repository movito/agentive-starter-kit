"""Tests for scripts/core/check_cross_repo_config.py."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "core"))

from check_cross_repo_config import (  # noqa: E402
    FAIL,
    MALFORMED,
    PASS,
    WARN,
    check,
    declares_cross_repo,
    main,
    parse_target_section,
)

TARGET_SECTION = """## Target Repository

- **Path**: `../my-app-code`
- **GitHub**: `movito/my-app-code`
"""

DECLARING_README = """# My App (planning)

The planning side of a cross-repo split. Application code lives in
`../my-app-code` (`movito/my-app-code` on GitHub).
"""


def _write_repo(tmp_path: Path, readme: str = "", claude: str = "") -> Path:
    if readme:
        (tmp_path / "README.md").write_text(readme, encoding="utf-8")
    if claude:
        (tmp_path / "CLAUDE.md").write_text(claude, encoding="utf-8")
    return tmp_path


# ── declares_cross_repo ──────────────────────────────────────────────


class TestDeclaresCrossRepo:
    def test_concrete_sibling_code_path_declares(self):
        assert declares_cross_repo("code lives in ../label-maker-code") is True

    def test_concrete_sibling_web_path_declares(self):
        assert declares_cross_repo("see ../foo-web for the app") is True

    def test_planning_split_prose_declares(self):
        assert declares_cross_repo("The planning side of a cross-repo split.") is True

    def test_placeholder_stem_does_not_declare(self):
        assert declares_cross_repo("e.g. `../my-project-code`") is False

    def test_your_project_placeholder_does_not_declare(self):
        assert declares_cross_repo("`../your-project-code`") is False

    def test_abstract_mention_does_not_declare(self):
        # Tooling that references the pattern without a concrete pair.
        text = "grep '## Target Repository' CLAUDE.md || echo SINGLE_REPO_MODE"
        assert declares_cross_repo(text) is False

    def test_empty_text_does_not_declare(self):
        assert declares_cross_repo("") is False


# ── parse_target_section ─────────────────────────────────────────────


class TestParseTargetSection:
    def test_absent_heading_returns_none(self):
        assert parse_target_section("# Title\n\nNo section here.") is None

    def test_parseable_section(self):
        result = parse_target_section(TARGET_SECTION)
        assert result == {"path": "../my-app-code", "github": "movito/my-app-code"}

    def test_missing_github_is_malformed(self):
        text = "## Target Repository\n\n- **Path**: `../x-code`\n"
        assert parse_target_section(text) == MALFORMED

    def test_missing_path_is_malformed(self):
        text = "## Target Repository\n\n- **GitHub**: `o/x-code`\n"
        assert parse_target_section(text) == MALFORMED

    def test_section_stops_at_next_heading(self):
        text = (
            "## Target Repository\n\n"
            "- **Path**: `../x-code`\n\n"
            "## Other\n\n"
            "- **GitHub**: `o/should-not-be-found`\n"
        )
        # GitHub lives under a different heading, so the section is malformed.
        assert parse_target_section(text) == MALFORMED

    def test_unbackticked_values_parse(self):
        text = "## Target Repository\n\n- **Path**: ../x-code\n- **GitHub**: o/x-code\n"
        result = parse_target_section(text)
        assert result == {"path": "../x-code", "github": "o/x-code"}


# ── check (integration) ──────────────────────────────────────────────


class TestCheck:
    def test_single_repo_no_declaration_passes(self, tmp_path):
        repo = _write_repo(tmp_path, readme="# Tool\n\nA single-repo project.")
        result = check(repo)
        assert result.status == PASS

    def test_declared_but_no_section_fails(self, tmp_path):
        repo = _write_repo(tmp_path, readme=DECLARING_README)
        result = check(repo)
        assert result.status == FAIL
        assert "Target Repository" in result.message

    def test_declared_with_malformed_section_fails(self, tmp_path):
        claude = "## Target Repository\n\n- **Path**: `../my-app-code`\n"
        repo = _write_repo(tmp_path, readme=DECLARING_README, claude=claude)
        result = check(repo)
        assert result.status == FAIL
        assert "missing Path or GitHub" in result.message

    def test_section_present_path_missing_warns(self, tmp_path):
        # Nest the repo so '../my-app-code' resolves inside this test's
        # isolated tmp_path (and does NOT exist).
        repo = (tmp_path / "planning").resolve()
        repo.mkdir()
        _write_repo(repo, readme=DECLARING_README, claude=TARGET_SECTION)
        result = check(repo)
        assert result.status == WARN
        assert "not checked out locally" in result.message

    def test_section_present_path_exists_passes(self, tmp_path):
        repo = (tmp_path / "planning").resolve()
        repo.mkdir()
        # Create the sibling target so '../my-app-code' resolves.
        (tmp_path / "my-app-code").mkdir()
        _write_repo(repo, readme=DECLARING_README, claude=TARGET_SECTION)
        result = check(repo)
        assert result.status == PASS
        assert "present" in result.message

    def test_no_files_passes(self, tmp_path):
        result = check(tmp_path)
        assert result.status == PASS

    def test_declaration_in_claude_only_still_checked(self, tmp_path):
        # Declaration via CLAUDE.md prose, no parseable section -> FAIL.
        claude = "The planning side of a cross-repo split.\n"
        repo = _write_repo(tmp_path, claude=claude)
        result = check(repo)
        assert result.status == FAIL

    def test_unreadable_file_treated_as_empty(self, tmp_path, monkeypatch):
        # A read error must not crash the check; it degrades to "absent".
        def boom(self, *args, **kwargs):
            raise OSError("permission denied")

        monkeypatch.setattr(Path, "read_text", boom)
        result = check(tmp_path)
        assert result.status == PASS


# ── main() CLI ───────────────────────────────────────────────────────


class TestMain:
    def _run(self, monkeypatch, argv):
        monkeypatch.setattr(sys, "argv", argv)
        try:
            main()
        except SystemExit as exc:
            return exc.code
        return 0

    def test_main_pass_exits_zero(self, tmp_path, monkeypatch, capsys):
        _write_repo(tmp_path, readme="# Tool\n\nSingle repo.")
        code = self._run(monkeypatch, ["prog", str(tmp_path)])
        assert code == 0
        assert "✅" in capsys.readouterr().out

    def test_main_fail_exits_one(self, tmp_path, monkeypatch, capsys):
        _write_repo(tmp_path, readme=DECLARING_README)
        code = self._run(monkeypatch, ["prog", str(tmp_path)])
        assert code == 1
        assert "FAILED" in capsys.readouterr().out

    def test_main_warn_exits_zero(self, tmp_path, monkeypatch, capsys):
        repo = (tmp_path / "planning").resolve()
        repo.mkdir()
        _write_repo(repo, readme=DECLARING_README, claude=TARGET_SECTION)
        code = self._run(monkeypatch, ["prog", str(repo)])
        assert code == 0
        assert "warning" in capsys.readouterr().out

    def test_main_defaults_to_cwd(self, tmp_path, monkeypatch):
        _write_repo(tmp_path, readme="# Tool\n\nSingle repo.")
        monkeypatch.chdir(tmp_path)
        code = self._run(monkeypatch, ["prog"])
        assert code == 0
