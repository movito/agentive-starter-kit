"""Port-specific unit tests for agentive_kit.preflight (KIT-0091).

The behavior contract lives in tests/test_preflight_check.py (the F2
parity matrix, driving bash shim and module through identical stub-gh
scenarios). This module covers only what the matrix cannot express:
edges of internal helpers the harness never routes through (CRLF
cross-repo config, poll-delay clamping).
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "agentive_kit", reason="agentive-kit package source present only in the kit repo"
)

from agentive_kit import preflight  # noqa: E402

TARGET_SECTION = (
    "# Project\n"
    "\n"
    "## Target Repository\n"
    "\n"
    "- **Path**: `../sibling-repo`\n"
    "- **GitHub**: `owner/sibling-repo`\n"
    "\n"
    "## Next Section\n"
)


class TestParseTargetRepo:
    def _root(self, tmp_path, text):
        (tmp_path / "CLAUDE.md").write_text(text, encoding="utf-8")
        return tmp_path

    def test_lf_section_parsed(self, tmp_path, capsys):
        root = self._root(tmp_path, TARGET_SECTION)
        target = preflight._parse_target_repo(root, "")
        assert target.repo == "owner/sibling-repo"
        assert target.path == "../sibling-repo"

    def test_crlf_section_parsed(self, tmp_path, capsys):
        # o3 (PR 1 round 2): the bash awk header pattern's [[:space:]]*
        # swallowed a CR, so CRLF-checked-out CLAUDE.md files worked —
        # the port must match them too.
        root = self._root(tmp_path, TARGET_SECTION.replace("\n", "\r\n"))
        target = preflight._parse_target_repo(root, "")
        assert target.repo == "owner/sibling-repo"
        assert target.path == "../sibling-repo"

    def test_no_section_is_single_repo(self, tmp_path):
        root = self._root(tmp_path, "# Project\n\nNo target section here.\n")
        target = preflight._parse_target_repo(root, "")
        assert target.repo == ""
        assert target.path == ""

    def test_override_wins_and_leaves_path_empty(self, tmp_path):
        root = self._root(tmp_path, TARGET_SECTION)
        target = preflight._parse_target_repo(root, "other/repo")
        assert target.repo == "other/repo"
        assert target.path == ""

    def test_malformed_slug_from_claude_md_refused(self, tmp_path, capsys):
        root = self._root(
            tmp_path,
            "## Target Repository\n- **GitHub**: `not a slug`\n",
        )
        with pytest.raises(SystemExit) as excinfo:
            preflight._parse_target_repo(root, "")
        assert excinfo.value.code == 1
        assert "owner/name format" in capsys.readouterr().err


class TestPollDelay:
    def test_default_when_unset(self, monkeypatch):
        monkeypatch.delenv("PREFLIGHT_CI_POLL_DELAY", raising=False)
        assert preflight._poll_delay() == float(preflight.CI_POLL_DELAY)

    def test_env_value_used(self, monkeypatch):
        monkeypatch.setenv("PREFLIGHT_CI_POLL_DELAY", "2.5")
        assert preflight._poll_delay() == 2.5

    def test_non_numeric_falls_back(self, monkeypatch):
        monkeypatch.setenv("PREFLIGHT_CI_POLL_DELAY", "soon")
        assert preflight._poll_delay() == float(preflight.CI_POLL_DELAY)

    def test_negative_clamps_to_zero(self, monkeypatch):
        # time.sleep raises ValueError on negatives — gate code must
        # never crash on a bad seam value (o3, PR 1 round 2).
        monkeypatch.setenv("PREFLIGHT_CI_POLL_DELAY", "-5")
        assert preflight._poll_delay() == 0.0
