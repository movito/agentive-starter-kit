"""Tests for scripts/.core-manifest.json — structure and file existence validation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "scripts" / ".core-manifest.json"

REQUIRED_TOP_LEVEL_KEYS = {
    "core_version",
    "source_repo",
    "synced_at",
    "files",
    "opted_in",
}
KNOWN_TIERS = {"scripts_core", "commands_core", "commands_optional"}

# Where each tier's files live relative to the repo root
TIER_BASE_PATHS = {
    "scripts_core": REPO_ROOT / "scripts",
    "commands_core": REPO_ROOT / ".claude" / "commands",
    "commands_optional": REPO_ROOT / ".kit" / "commands",
}


@pytest.fixture
def manifest():
    """Load and return the parsed manifest."""
    assert MANIFEST_PATH.exists(), f"Manifest not found at {MANIFEST_PATH}"
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


class TestManifestStructure:
    def test_has_required_keys(self, manifest):
        missing = REQUIRED_TOP_LEVEL_KEYS - set(manifest.keys())
        assert not missing, f"Missing top-level keys: {missing}"

    def test_core_version_is_semver(self, manifest):
        version = manifest["core_version"]
        parts = version.split(".")
        assert len(parts) == 3, f"Version {version} is not semver (expected X.Y.Z)"
        for part in parts:
            assert part.isdigit(), f"Version component {part!r} is not numeric"

    def test_source_repo_format(self, manifest):
        repo = manifest["source_repo"]
        assert "/" in repo, f"source_repo should be owner/name format, got {repo!r}"

    def test_synced_at_is_iso_timestamp(self, manifest):
        ts = manifest["synced_at"]
        assert ts.endswith("Z"), f"synced_at should end with Z, got {ts!r}"
        assert "T" in ts, f"synced_at should be ISO format, got {ts!r}"

    def test_files_is_dict_with_known_tiers(self, manifest):
        files = manifest["files"]
        assert isinstance(files, dict), "files should be a dict"
        unknown = set(files.keys()) - KNOWN_TIERS
        assert not unknown, f"Unknown tiers in manifest: {unknown}"

    def test_opted_in_references_valid_tiers(self, manifest):
        opted_in = manifest["opted_in"]
        assert isinstance(opted_in, list), "opted_in should be a list"
        files_keys = set(manifest["files"].keys())
        for tier in opted_in:
            assert tier in files_keys, f"opted_in references unknown tier: {tier!r}"

    def test_opted_in_does_not_include_core_tiers(self, manifest):
        """Core tiers are always synced; opting in to them is redundant."""
        for tier in manifest["opted_in"]:
            assert not tier.endswith(
                "_core"
            ), f"Core tier {tier!r} in opted_in is redundant — core tiers always sync"


class TestManifestFileExistence:
    def test_all_scripts_core_files_exist(self, manifest):
        base = TIER_BASE_PATHS["scripts_core"]
        for entry in manifest["files"]["scripts_core"]:
            path = base / entry
            assert (
                path.exists()
            ), f"scripts_core entry missing on disk: {entry} (expected at {path})"

    def test_all_commands_core_files_exist(self, manifest):
        base = TIER_BASE_PATHS["commands_core"]
        for entry in manifest["files"]["commands_core"]:
            path = base / entry
            assert (
                path.exists()
            ), f"commands_core entry missing on disk: {entry} (expected at {path})"

    def test_all_commands_optional_files_exist(self, manifest):
        base = TIER_BASE_PATHS["commands_optional"]
        for entry in manifest["files"]["commands_optional"]:
            path = base / entry
            assert (
                path.exists()
            ), f"commands_optional entry missing on disk: {entry} (expected at {path})"


class TestManifestConsistency:
    def test_no_duplicate_entries_within_tiers(self, manifest):
        for tier, entries in manifest["files"].items():
            seen = set()
            for entry in entries:
                assert entry not in seen, f"Duplicate entry in {tier}: {entry!r}"
                seen.add(entry)

    def test_no_duplicate_entries_across_tiers(self, manifest):
        seen = {}
        for tier, entries in manifest["files"].items():
            for entry in entries:
                assert (
                    entry not in seen
                ), f"Entry {entry!r} in both {seen[entry]!r} and {tier!r}"
                seen[entry] = tier

    def test_scripts_core_count(self, manifest):
        count = len(manifest["files"]["scripts_core"])
        assert count == 14, f"Expected 14 scripts_core entries, got {count}"

    def test_commands_core_count(self, manifest):
        count = len(manifest["files"]["commands_core"])
        assert count == 6, f"Expected 6 commands_core entries, got {count}"

    def test_commands_optional_count(self, manifest):
        count = len(manifest["files"]["commands_optional"])
        assert count == 5, f"Expected 5 commands_optional entries, got {count}"

    def test_total_entry_count(self, manifest):
        total = sum(len(entries) for entries in manifest["files"].values())
        assert total == 25, f"Expected 25 total entries, got {total}"
