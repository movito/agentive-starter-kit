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
