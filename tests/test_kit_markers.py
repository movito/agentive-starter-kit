"""Tests for scripts/local/kit_markers.py — KIT-LOCAL marker merge logic.

These guard the heart of KIT-0033: a re-bootstrap must refresh agent
structure *outside* the markers while preserving consumer content
*inside* them byte-for-byte (requirements F4 + N2).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
_MODULE_PATH = REPO_ROOT / "scripts" / "local" / "kit_markers.py"

# kit_markers.py is an ASK-only bootstrap tool (scripts/local is not synced
# downstream). The consumer sync also excludes this test, but guard the load
# so a stray copy in a consumer checkout skips cleanly instead of erroring at
# collection.
if not _MODULE_PATH.exists():
    pytest.skip("kit_markers.py present only in the kit repo", allow_module_level=True)

_spec = importlib.util.spec_from_file_location("kit_markers", _MODULE_PATH)
km = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(km)


SAMPLE = """# Agent

## Project Context

> instructions stay outside

<!-- BEGIN KIT-LOCAL: project-context -->
ASK content here
- a bullet
<!-- END KIT-LOCAL: project-context -->

## Stack Notes

<!-- BEGIN KIT-LOCAL: stack-notes -->
- pytest + DK rules
<!-- END KIT-LOCAL: stack-notes -->

## Phase 4
done
"""


class TestFindRegions:
    def test_returns_names_in_order(self):
        assert km.find_regions(SAMPLE) == ["project-context", "stack-notes"]

    def test_empty_when_no_markers(self):
        assert km.find_regions("# plain doc\n") == []


class TestExtractRegion:
    def test_extracts_inner_content(self):
        assert km.extract_region(SAMPLE, "project-context") == (
            "ASK content here\n- a bullet"
        )

    def test_missing_region_returns_none(self):
        assert km.extract_region(SAMPLE, "nope") is None


class TestReplaceRegion:
    def test_replaces_inner_preserving_markers(self):
        out = km.replace_region(SAMPLE, "stack-notes", "- cargo test")
        assert "<!-- BEGIN KIT-LOCAL: stack-notes -->\n- cargo test\n" in out
        assert "<!-- END KIT-LOCAL: stack-notes -->" in out
        # other region untouched
        assert (
            km.extract_region(out, "project-context") == "ASK content here\n- a bullet"
        )

    def test_round_trip_is_byte_identical(self):
        body = km.extract_region(SAMPLE, "project-context")
        assert km.replace_region(SAMPLE, "project-context", body) == SAMPLE

    def test_missing_region_raises(self):
        with pytest.raises(KeyError):
            km.replace_region(SAMPLE, "nope", "x")

    def test_replaces_every_occurrence_of_a_name(self):
        # A malformed file with two same-named regions: both must update,
        # not just the first (no silent skip).
        dupe = (
            "<!-- BEGIN KIT-LOCAL: r -->\nold-1\n<!-- END KIT-LOCAL: r -->\n"
            "<!-- BEGIN KIT-LOCAL: r -->\nold-2\n<!-- END KIT-LOCAL: r -->\n"
        )
        out = km.replace_region(dupe, "r", "NEW")
        assert out.count("NEW") == 2
        assert "old-1" not in out and "old-2" not in out


class TestMerge:
    def test_fresh_fills_placeholders(self):
        placeholders = {"project-context": "PH-PC", "stack-notes": "PH-SN"}
        out = km.merge(SAMPLE, consumer=None, placeholders=placeholders)
        assert km.extract_region(out, "project-context") == "PH-PC"
        assert km.extract_region(out, "stack-notes") == "PH-SN"

    def test_rebootstrap_preserves_consumer_content(self):
        # Consumer customized both regions.
        consumer = km.replace_region(SAMPLE, "project-context", "WIDGET FACTORY")
        consumer = km.replace_region(consumer, "stack-notes", "cargo only")
        # Upstream changed OUTSIDE the markers.
        upstream = SAMPLE.replace("## Phase 4", "## Phase 4: Self-Review (GATE)")
        out = km.merge(upstream, consumer=consumer, placeholders=None)
        # Inside-marker content preserved byte-identical...
        assert km.extract_region(out, "project-context") == "WIDGET FACTORY"
        assert km.extract_region(out, "stack-notes") == "cargo only"
        # ...and the upstream structural change outside markers is picked up.
        assert "## Phase 4: Self-Review (GATE)" in out

    def test_consumer_takes_priority_over_placeholder(self):
        consumer = km.replace_region(SAMPLE, "project-context", "KEEP ME")
        out = km.merge(
            SAMPLE,
            consumer=consumer,
            placeholders={"project-context": "SHOULD-NOT-WIN"},
        )
        assert km.extract_region(out, "project-context") == "KEEP ME"

    def test_no_consumer_no_placeholder_keeps_upstream(self):
        out = km.merge(SAMPLE, consumer=None, placeholders=None)
        assert out == SAMPLE

    def test_malformed_consumer_marker_raises(self):
        # Consumer file opened a region but the END marker was edited away;
        # merge must fail fast rather than clobber the trapped content.
        malformed = (
            "<!-- BEGIN KIT-LOCAL: project-context -->\n"
            "consumer content with no closing marker\n"
        )
        with pytest.raises(ValueError, match="malformed KIT-LOCAL region"):
            km.merge(SAMPLE, consumer=malformed, placeholders={"project-context": "X"})

    def test_markerless_consumer_falls_back_to_placeholder(self):
        # A consumer stuck on a pre-consolidation agent has no markers;
        # the region must seed from the placeholder, NOT inherit the
        # upstream (kit) content — otherwise kit identity leaks.
        markerless = "# old agent\n\nno markers here at all\n"
        out = km.merge(
            SAMPLE,
            consumer=markerless,
            placeholders={"project-context": "PH-PC", "stack-notes": "PH-SN"},
        )
        assert km.extract_region(out, "project-context") == "PH-PC"
        assert km.extract_region(out, "stack-notes") == "PH-SN"
        assert "ASK content here" not in out


class TestDefaultPlaceholders:
    def test_has_both_regions(self):
        ph = km.default_placeholders("my-app")
        assert set(ph) == {"project-context", "stack-notes"}

    def test_title_cased_from_project_name(self):
        ph = km.default_placeholders("widget-factory_2")
        assert "Widget Factory 2" in ph["project-context"]

    def test_no_kit_identity_leaks(self):
        ph = km.default_placeholders("my-app")
        blob = ph["project-context"] + ph["stack-notes"]
        for needle in ("agentive-starter-kit", "KIT-NNNN", "pytest-fast", "DK rules"):
            assert needle not in blob

    @pytest.mark.parametrize("name", ["", "---", "___", "  "])
    def test_blank_name_falls_back_to_readable_title(self, name):
        ph = km.default_placeholders(name)
        assert "**Your Project**" in ph["project-context"]
        assert "****" not in ph["project-context"]


class TestRealAgentFiles:
    """The shipped agents must expose the expected regions and round-trip."""

    @pytest.mark.parametrize(
        "rel,expected",
        [
            (".claude/agents/feature-developer.md", ["project-context", "stack-notes"]),
            (".claude/agents/planner.md", ["project-context"]),
        ],
    )
    def test_regions_present(self, rel, expected):
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert km.find_regions(text) == expected

    @pytest.mark.parametrize(
        "rel",
        [".claude/agents/feature-developer.md", ".claude/agents/planner.md"],
    )
    def test_round_trip_identity(self, rel):
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        out = text
        for name in km.find_regions(text):
            out = km.replace_region(out, name, km.extract_region(text, name))
        assert out == text


class TestCLI:
    """Exercise the argparse CLI surface (main + _cmd_* handlers)."""

    def _write(self, path, text):
        path.write_text(text, encoding="utf-8")
        return str(path)

    def test_merge_fresh_with_project_name(self, tmp_path):
        up = self._write(tmp_path / "up.md", SAMPLE)
        out = str(tmp_path / "out.md")
        rc = km.main(
            ["merge", "--upstream", up, "--out", out, "--project-name", "demo"]
        )
        assert rc == 0
        merged = (tmp_path / "out.md").read_text(encoding="utf-8")
        assert "**Demo**" in km.extract_region(merged, "project-context")

    def test_merge_rebootstrap_preserves_consumer(self, tmp_path):
        up = self._write(tmp_path / "up.md", SAMPLE)
        consumer_text = km.replace_region(SAMPLE, "project-context", "KEEP")
        cons = self._write(tmp_path / "cons.md", consumer_text)
        out = str(tmp_path / "out.md")
        rc = km.main(
            [
                "merge",
                "--upstream",
                up,
                "--out",
                out,
                "--consumer",
                cons,
                "--project-name",
                "demo",
            ]
        )
        assert rc == 0
        merged = (tmp_path / "out.md").read_text(encoding="utf-8")
        assert km.extract_region(merged, "project-context") == "KEEP"

    def test_merge_missing_consumer_path_is_ignored(self, tmp_path):
        up = self._write(tmp_path / "up.md", SAMPLE)
        out = str(tmp_path / "out.md")
        rc = km.main(
            [
                "merge",
                "--upstream",
                up,
                "--out",
                out,
                "--consumer",
                str(tmp_path / "nope.md"),
                "--project-name",
                "demo",
            ]
        )
        assert rc == 0  # absent consumer file falls back to placeholders

    def test_extract_prints_body(self, tmp_path, capsys):
        f = self._write(tmp_path / "a.md", SAMPLE)
        rc = km.main(["extract", f, "project-context"])
        assert rc == 0
        assert capsys.readouterr().out == "ASK content here\n- a bullet"

    def test_extract_missing_region_returns_1(self, tmp_path):
        f = self._write(tmp_path / "a.md", SAMPLE)
        assert km.main(["extract", f, "nope"]) == 1

    def test_replace_from_content_file(self, tmp_path):
        f = self._write(tmp_path / "a.md", SAMPLE)
        cf = self._write(tmp_path / "c.txt", "REPLACED")
        rc = km.main(["replace", f, "stack-notes", "--content-file", cf])
        assert rc == 0
        text = (tmp_path / "a.md").read_text(encoding="utf-8")
        assert km.extract_region(text, "stack-notes") == "REPLACED"

    def test_replace_from_stdin(self, tmp_path, monkeypatch):
        import io

        f = self._write(tmp_path / "a.md", SAMPLE)
        monkeypatch.setattr("sys.stdin", io.StringIO("VIA-STDIN"))
        rc = km.main(["replace", f, "stack-notes", "--stdin"])
        assert rc == 0
        text = (tmp_path / "a.md").read_text(encoding="utf-8")
        assert km.extract_region(text, "stack-notes") == "VIA-STDIN"

    def test_replace_missing_region_returns_1(self, tmp_path):
        f = self._write(tmp_path / "a.md", SAMPLE)
        assert km.main(["replace", f, "nope", "--content-file", f]) == 1

    def test_regions_lists_names(self, tmp_path, capsys):
        f = self._write(tmp_path / "a.md", SAMPLE)
        rc = km.main(["regions", f])
        assert rc == 0
        assert capsys.readouterr().out.split() == ["project-context", "stack-notes"]
