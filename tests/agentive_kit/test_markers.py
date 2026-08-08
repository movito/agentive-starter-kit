"""Tests for agentive_kit.markers — the package's region READER (KIT-0091).

The authoritative grammar lives in scripts/local/kit_markers.py (the
writer). The package carries a minimal read-only port; the conformance
class below pins the two against each other on the tricky cases so
they cannot drift apart silently. Module-skips on consumer checkouts
where scripts/local is absent (the test_kit_markers.py pattern).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

pytest.importorskip(
    "agentive_kit", reason="agentive-kit package source present only in the kit repo"
)

from agentive_kit import markers  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_KIT_MARKERS = REPO_ROOT / "scripts" / "local" / "kit_markers.py"

REGION = (
    "# heading\n"
    "<!-- BEGIN KIT-LOCAL: kit-install -->\n"
    "shape: single\n"
    "bots: none\n"
    "<!-- END KIT-LOCAL: kit-install -->\n"
)


class TestExtractRegion:
    def test_basic_extraction(self):
        assert markers.extract_region(REGION, "kit-install") == (
            "shape: single\nbots: none"
        )

    def test_absent_region_is_none(self):
        assert markers.extract_region(REGION, "stack-notes") is None

    def test_whitespace_drift_in_markers_tolerated(self):
        text = (
            "<!--  BEGIN   KIT-LOCAL:  kit-install  -->\n"
            "bots: coderabbit\n"
            "<!--  END   KIT-LOCAL:  kit-install  -->\n"
        )
        assert markers.extract_region(text, "kit-install") == "bots: coderabbit"

    def test_crlf_file_parses(self):
        text = (
            "<!-- BEGIN KIT-LOCAL: kit-install -->\r\n"
            "bots: none\r\n"
            "<!-- END KIT-LOCAL: kit-install -->\r\n"
        )
        assert markers.extract_region(text, "kit-install") == "bots: none"

    def test_prefix_named_sibling_region_not_confused(self):
        text = (
            "<!-- BEGIN KIT-LOCAL: kit-install-extra -->\n"
            "wrong\n"
            "<!-- END KIT-LOCAL: kit-install-extra -->\n" + REGION
        )
        assert markers.extract_region(text, "kit-install") == (
            "shape: single\nbots: none"
        )


@pytest.fixture(scope="module")
def kit_markers():
    spec = importlib.util.spec_from_file_location("_kit_markers", _KIT_MARKERS)
    module = importlib.util.module_from_spec(spec)
    # register before exec so dataclass/typing lookups inside the
    # module resolve normally
    sys.modules["_kit_markers"] = module
    try:
        spec.loader.exec_module(module)
        yield module
    finally:
        sys.modules.pop("_kit_markers", None)


@pytest.mark.skipif(
    not _KIT_MARKERS.exists(), reason="kit_markers.py absent (consumer checkout)"
)
class TestConformanceWithKitMarkers:
    """The package reader and the repo tool must agree byte-for-byte."""

    @pytest.mark.parametrize(
        "text",
        [
            REGION,
            "no regions here\n",
            "<!-- BEGIN KIT-LOCAL: kit-install -->\n"
            "<!-- END KIT-LOCAL: kit-install -->\n",
            "  <!-- BEGIN KIT-LOCAL: kit-install -->  \n"
            "indented markers\n"
            "  <!-- END KIT-LOCAL: kit-install -->\n",
            "<!-- BEGIN KIT-LOCAL: kit-install -->\r\n"
            "bots: bugbot\r\n"
            "<!-- END KIT-LOCAL: kit-install -->\r\n",
            # damaged END marker: neither reader should match
            "<!-- BEGIN KIT-LOCAL: kit-install -->\n"
            "bots: none\n"
            "<!-- END KIT-LOCAL: other -->\n",
        ],
        ids=["basic", "absent", "empty-body", "indented", "crlf", "damaged-end"],
    )
    def test_extract_agrees(self, kit_markers, text):
        assert markers.extract_region(text, "kit-install") == (
            kit_markers.extract_region(text, "kit-install")
        )
