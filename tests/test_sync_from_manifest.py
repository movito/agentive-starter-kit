"""Tests for scripts/core/sync_from_manifest.py — the Channel B sync engine.

Coverage (KIT-0036 D2):

* Characterization: fixture source+target trees in → tree-level property
  assertions out (files present, content, manifest fields), not gold-file
  console output.
* Dual-entrypoint contract: the same fixture through the library API
  (``sync()``) and through the CLI (as the Action calls it) produces
  identical trees and manifests. PR 2 extends this to ``project sync``.
* Self-sync: a source whose ``sync_from_manifest.py`` is modified upgrades
  the target's engine file — the scenario production always hits.
* Exit-code contract frozen: 0/1/2/3/4.
* Edge cases: fresh consumer, unrecognized schema, ``--only`` slash forms,
  opted_in preservation, partial_sync set/cleared, directory shrink.
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

ENGINE = (
    Path(__file__).resolve().parent.parent
    / "scripts"
    / "core"
    / "sync_from_manifest.py"
)
sys.path.insert(0, str(ENGINE.parent))

from sync_from_manifest import (  # noqa: E402
    EXIT_MANIFEST,
    EXIT_SOURCE,
    EXIT_USAGE,
    ManifestError,
    SourceError,
    SyncOptions,
    UsageError,
    main,
    sync,
)

# ── Fixture builders ────────────────────────────────────────────────────────
BASE_MANIFEST = {
    "core_version": "1.0.0",
    "source_repo": "movito/test-kit",
    "synced_at": "2026-01-01T00:00:00Z",
    "files": {
        "scripts_core": ["core/foo.sh", "core/bar.py"],
        "commands_core": ["cmd.md"],
        "commands_optional": ["opt.md"],
        "kit_builder": [".kit/things/"],
    },
    "opted_in": [],
}


def _write(path: Path, text: str, *, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if mode is not None:
        os.chmod(path, mode)


def build_source(root: Path, *, manifest: dict | None = None) -> Path:
    """Build a minimal but complete source tree with all four tiers."""
    data = json.loads(json.dumps(manifest or BASE_MANIFEST))
    _write(
        root / "scripts" / ".core-manifest.json",
        json.dumps(data, indent=2) + "\n",
    )
    _write(root / "scripts" / "core" / "foo.sh", "#!/bin/sh\necho foo\n", mode=0o755)
    _write(root / "scripts" / "core" / "bar.py", "print('bar')\n")
    _write(root / ".claude" / "commands" / "cmd.md", "# cmd\n")
    _write(root / ".claude" / "commands" / "opt.md", "# opt\n")
    _write(root / ".kit" / "things" / "a.md", "alpha\n")
    _write(root / ".kit" / "things" / "b.md", "bravo\n")
    return root


def read_manifest(root: Path) -> dict:
    with open(root / "scripts" / ".core-manifest.json", encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture
def source(tmp_path: Path) -> Path:
    return build_source(tmp_path / "source")


@pytest.fixture
def target(tmp_path: Path) -> Path:
    (tmp_path / "target").mkdir()
    return tmp_path / "target"


# ── Characterization: full sync to a fresh consumer ─────────────────────────
class TestFullSyncFreshConsumer:
    def test_core_tiers_land_but_optional_and_builder_do_not(self, source, target):
        report = sync(source, target, SyncOptions())

        # Core tiers always sync.
        assert (target / "scripts" / "core" / "foo.sh").read_text(
            encoding="utf-8"
        ) == "#!/bin/sh\necho foo\n"
        assert (target / "scripts" / "core" / "bar.py").exists()
        assert (target / ".claude" / "commands" / "cmd.md").exists()
        # Optional not opted in; kit_builder needs --is-kit.
        assert not (target / ".claude" / "commands" / "opt.md").exists()
        assert not (target / ".kit" / "things").exists()
        assert report.status == "applied"
        assert report.complete is True

    def test_executable_bit_preserved(self, source, target):
        sync(source, target, SyncOptions())
        mode = stat.S_IMODE((target / "scripts" / "core" / "foo.sh").stat().st_mode)
        assert mode & 0o111, "executable bit should survive the sync"

    def test_mode_only_change_is_drift(self, source, target):
        # Content identical but the exec bit was stripped downstream: a real
        # run would restore it via chmod, so drift detection must flag it.
        sync(source, target, SyncOptions())
        script = target / "scripts" / "core" / "foo.sh"
        os.chmod(script, 0o644)  # strip exec bit
        report = sync(source, target, SyncOptions(dry_run=True))
        assert report.status == "drift"
        assert "scripts/core/foo.sh" in report.modified

    def test_is_kit_pulls_builder_tier(self, source, target):
        sync(source, target, SyncOptions(is_kit=True))
        assert (target / ".kit" / "things" / "a.md").read_text(
            encoding="utf-8"
        ) == "alpha\n"
        assert (target / ".kit" / "things" / "b.md").exists()

    def test_opt_in_pulls_optional_tier(self, source, target):
        manifest = json.loads(json.dumps(BASE_MANIFEST))
        # Target opts in via its own manifest.
        _write(
            target / "scripts" / ".core-manifest.json",
            json.dumps({**manifest, "opted_in": ["commands_optional"]}, indent=2),
        )
        sync(source, target, SyncOptions())
        assert (target / ".claude" / "commands" / "opt.md").exists()

    def test_fresh_consumer_manifest_written(self, source, target):
        sync(source, target, SyncOptions(is_kit=True))
        manifest = read_manifest(target)
        assert manifest["core_version"] == "1.0.0"
        assert manifest["opted_in"] == []
        assert "partial_sync" not in manifest

    def test_target_directory_created_if_missing(self, source, tmp_path):
        missing = tmp_path / "does" / "not" / "exist"
        assert not missing.exists()
        report = sync(source, missing, SyncOptions())
        assert report.status == "applied"
        assert (missing / "scripts" / "core" / "foo.sh").exists()


# ── opted_in preservation ───────────────────────────────────────────────────
class TestOptedInPreservation:
    def test_opted_in_preserved_verbatim(self, source, target):
        _write(
            target / "scripts" / ".core-manifest.json",
            json.dumps({**BASE_MANIFEST, "opted_in": ["commands_optional"]}, indent=2),
        )
        sync(source, target, SyncOptions())
        assert read_manifest(target)["opted_in"] == ["commands_optional"]


# ── Idempotency and dry-run ─────────────────────────────────────────────────
class TestIdempotencyAndDryRun:
    def test_second_run_is_clean(self, source, target):
        sync(source, target, SyncOptions(is_kit=True))
        report = sync(source, target, SyncOptions(is_kit=True))
        assert report.status == "clean"
        assert report.added == []
        assert report.modified == []

    def test_dry_run_writes_nothing(self, source, target):
        report = sync(source, target, SyncOptions(is_kit=True, dry_run=True))
        assert report.status == "drift"
        assert not (target / "scripts" / "core" / "foo.sh").exists()
        assert not (target / "scripts" / ".core-manifest.json").exists()

    def test_dry_run_reports_completeness_verdict(self, source, target):
        report = sync(source, target, SyncOptions(is_kit=True, dry_run=True))
        assert report.would_bump_core_version is True
        assert report.would_set_partial_sync is False

    def test_dry_run_flags_version_only_drift(self, source, target):
        # Files identical, but upstream bumped core_version: a real run would
        # rewrite the manifest, so dry-run must report drift (not clean).
        sync(source, target, SyncOptions(is_kit=True))
        newer = json.loads(json.dumps(BASE_MANIFEST))
        newer["core_version"] = "2.0.0"
        source2 = build_source(target.parent / "source2", manifest=newer)
        report = sync(source2, target, SyncOptions(is_kit=True, dry_run=True))
        assert report.added == []
        assert report.modified == []
        assert report.status == "drift"
        assert report.would_bump_core_version is True


# ── Partial sync + partial_sync marker ──────────────────────────────────────
class TestPartialSync:
    def test_tier_filter_is_partial_and_sets_marker(self, source, target):
        sync(source, target, SyncOptions(is_kit=True))  # full first
        report = sync(source, target, SyncOptions(tiers=["commands_core"], is_kit=True))
        assert report.complete is False
        assert read_manifest(target).get("partial_sync") is True

    def test_partial_leaves_core_version_untouched(self, source, target):
        # Full sync at 1.0.0.
        sync(source, target, SyncOptions(is_kit=True))
        # Upstream advances to 2.0.0; pull only one tier.
        newer = json.loads(json.dumps(BASE_MANIFEST))
        newer["core_version"] = "2.0.0"
        source2 = build_source(target.parent / "source2", manifest=newer)
        report = sync(source2, target, SyncOptions(tiers=["commands_core"]))
        assert report.complete is False
        assert read_manifest(target)["core_version"] == "1.0.0"

    def test_following_full_pull_clears_partial_and_bumps(self, source, target):
        sync(source, target, SyncOptions(is_kit=True))
        newer = json.loads(json.dumps(BASE_MANIFEST))
        newer["core_version"] = "2.0.0"
        source2 = build_source(target.parent / "source2", manifest=newer)
        sync(source2, target, SyncOptions(tiers=["commands_core"]))
        assert read_manifest(target).get("partial_sync") is True
        # Now a full pull.
        report = sync(source2, target, SyncOptions(is_kit=True))
        manifest = read_manifest(target)
        assert "partial_sync" not in manifest
        assert manifest["core_version"] == "2.0.0"
        assert report.would_bump_core_version is True


# ── Directory entry shrink (stale-file cleanup) ─────────────────────────────
class TestDirectoryShrink:
    def test_file_removed_upstream_disappears_downstream(self, source, target):
        sync(source, target, SyncOptions(is_kit=True))
        assert (target / ".kit" / "things" / "b.md").exists()
        # Upstream drops b.md from the directory.
        (source / ".kit" / "things" / "b.md").unlink()
        report = sync(source, target, SyncOptions(is_kit=True))
        assert not (target / ".kit" / "things" / "b.md").exists()
        assert (target / ".kit" / "things" / "a.md").exists()
        assert ".kit/things/b.md" in report.removed_files


# ── removed_entries (manifest-level removal) ────────────────────────────────
class TestRemovedEntries:
    def test_entry_dropped_upstream_is_reported(self, source, target):
        sync(source, target, SyncOptions(is_kit=True))
        # Upstream removes core/bar.py from the manifest entirely.
        newer = json.loads(json.dumps(BASE_MANIFEST))
        newer["files"]["scripts_core"] = ["core/foo.sh"]
        source2 = build_source(target.parent / "source2", manifest=newer)
        report = sync(source2, target, SyncOptions(is_kit=True))
        assert "core/bar.py" in report.removed_entries

    def test_removed_entry_self_clears_next_run(self, source, target):
        sync(source, target, SyncOptions(is_kit=True))
        newer = json.loads(json.dumps(BASE_MANIFEST))
        newer["files"]["scripts_core"] = ["core/foo.sh"]
        source2 = build_source(target.parent / "source2", manifest=newer)
        sync(source2, target, SyncOptions(is_kit=True))
        report = sync(source2, target, SyncOptions(is_kit=True))
        assert report.removed_entries == []


# ── Overwrite warning ───────────────────────────────────────────────────────
class TestOverwriteWarning:
    def test_untracked_target_file_triggers_warning(self, source, target):
        # Target has a manifest that does NOT list core/bar.py, but the file
        # exists on disk — sync is about to overwrite an untracked file.
        stale_manifest = json.loads(json.dumps(BASE_MANIFEST))
        stale_manifest["files"]["scripts_core"] = ["core/foo.sh"]
        _write(
            target / "scripts" / ".core-manifest.json",
            json.dumps(stale_manifest, indent=2),
        )
        _write(target / "scripts" / "core" / "bar.py", "print('local')\n")
        report = sync(source, target, SyncOptions())
        assert any("bar.py" in w for w in report.warnings)
        assert report.status == "applied_with_warnings"


# ── --only entry key semantics ──────────────────────────────────────────────
class TestOnlyFilter:
    def test_only_file_entry_accepted(self, source, target):
        report = sync(source, target, SyncOptions(only=["core/foo.sh"]))
        assert (target / "scripts" / "core" / "foo.sh").exists()
        assert not (target / "scripts" / "core" / "bar.py").exists()
        assert report.complete is False

    def test_only_directory_entry_with_slash_accepted(self, source, target):
        report = sync(source, target, SyncOptions(only=[".kit/things/"], is_kit=True))
        assert (target / ".kit" / "things" / "a.md").exists()
        assert report.complete is False

    def test_only_directory_without_slash_rejected(self, source, target):
        with pytest.raises(UsageError) as exc:
            sync(source, target, SyncOptions(only=[".kit/things"], is_kit=True))
        assert ".kit/things/" in str(exc.value)  # near-miss hint

    def test_only_unknown_key_rejected(self, source, target):
        with pytest.raises(UsageError):
            sync(source, target, SyncOptions(only=["core/nope.sh"]))

    def test_only_entry_in_non_entitled_tier_rejected(self, source, target):
        # opt.md is in commands_optional, which the fresh target has not
        # opted into — reachable in the manifest, but not entitled.
        with pytest.raises(UsageError):
            sync(source, target, SyncOptions(only=["opt.md"]))


# ── --tier validation ───────────────────────────────────────────────────────
class TestTierFilter:
    def test_unknown_tier_rejected(self, source, target):
        with pytest.raises(UsageError):
            sync(source, target, SyncOptions(tiers=["nonsense"]))

    def test_non_entitled_tier_rejected(self, source, target):
        with pytest.raises(UsageError):
            sync(source, target, SyncOptions(tiers=["kit_builder"]))  # no --is-kit


# ── Error classes / schema validation ───────────────────────────────────────
class TestErrors:
    def test_missing_source_raises_source_error(self, tmp_path, target):
        with pytest.raises(SourceError):
            sync(tmp_path / "nope", target, SyncOptions())

    def test_missing_source_manifest_raises_manifest_error(self, tmp_path, target):
        empty = tmp_path / "empty"
        (empty / "scripts").mkdir(parents=True)
        with pytest.raises(ManifestError):
            sync(empty, target, SyncOptions())

    def test_legacy_flat_array_manifest_rejected(self, tmp_path, target):
        # A ref predating the tiered manifest must fail loudly, not guess.
        legacy = tmp_path / "legacy"
        _write(
            legacy / "scripts" / ".core-manifest.json",
            json.dumps({"core_version": "0.1.0", "files": ["core/foo.sh"]}),
        )
        with pytest.raises(ManifestError):
            sync(legacy, target, SyncOptions())

    def test_malformed_json_manifest_rejected(self, tmp_path, target):
        bad = tmp_path / "bad"
        _write(bad / "scripts" / ".core-manifest.json", "{not json")
        with pytest.raises(ManifestError):
            sync(bad, target, SyncOptions())

    def test_corrupt_target_manifest_raises_not_silent_reset(self, source, target):
        # A corrupt (not absent) target manifest must fail loudly rather than
        # be treated as fresh — otherwise opted_in is silently reset to [].
        _write(target / "scripts" / ".core-manifest.json", "{corrupt")
        with pytest.raises(ManifestError):
            sync(source, target, SyncOptions())

    def test_non_object_target_manifest_raises(self, source, target):
        _write(target / "scripts" / ".core-manifest.json", "[1, 2, 3]")
        with pytest.raises(ManifestError):
            sync(source, target, SyncOptions())


# ── Exit-code contract (frozen) ─────────────────────────────────────────────
class TestExitCodes:
    def _run_cli(self, args: list[str]) -> int:
        return main(args)

    def test_clean_dry_run_exit_0(self, source, target):
        sync(source, target, SyncOptions(is_kit=True))
        code = self._run_cli(
            ["--source", str(source), "--target", str(target), "--is-kit", "--dry-run"]
        )
        assert code == 0

    def test_drift_dry_run_exit_1(self, source, target):
        code = self._run_cli(
            ["--source", str(source), "--target", str(target), "--is-kit", "--dry-run"]
        )
        assert code == 1

    def test_applied_exit_0(self, source, target):
        code = self._run_cli(
            ["--source", str(source), "--target", str(target), "--is-kit"]
        )
        assert code == 0

    def test_applied_with_warnings_exit_1(self, source, target):
        stale_manifest = json.loads(json.dumps(BASE_MANIFEST))
        stale_manifest["files"]["scripts_core"] = ["core/foo.sh"]
        _write(
            target / "scripts" / ".core-manifest.json",
            json.dumps(stale_manifest, indent=2),
        )
        _write(target / "scripts" / "core" / "bar.py", "print('local')\n")
        code = self._run_cli(["--source", str(source), "--target", str(target)])
        assert code == 1

    def test_usage_error_exit_2(self, source, target):
        code = self._run_cli(
            ["--source", str(source), "--target", str(target), "--only", "core/nope.sh"]
        )
        assert code == EXIT_USAGE

    def test_manifest_error_exit_3(self, tmp_path, target):
        empty = tmp_path / "empty"
        (empty / "scripts").mkdir(parents=True)
        code = self._run_cli(["--source", str(empty), "--target", str(target)])
        assert code == EXIT_MANIFEST

    def test_source_error_exit_4(self, tmp_path, target):
        code = self._run_cli(
            ["--source", str(tmp_path / "nope"), "--target", str(target)]
        )
        assert code == EXIT_SOURCE

    def test_report_json_written(self, source, target, tmp_path):
        out = tmp_path / "report.json"
        self._run_cli(
            [
                "--source",
                str(source),
                "--target",
                str(target),
                "--is-kit",
                "--dry-run",
                "--report-json",
                str(out),
            ]
        )
        report = json.loads(out.read_text(encoding="utf-8"))
        assert report["status"] == "drift"
        assert report["complete"] is True
        assert report["exit_code"] == 1


# ── Dual-entrypoint contract (PR 1 scope: library API vs CLI) ───────────────
class TestDualEntrypointContract:
    """Same fixture through sync() and through the CLI → identical results.

    PR 2 extends this with ``project sync`` as the third entrypoint, making it
    a true dual-*caller* test.
    """

    def _tree_snapshot(self, root: Path) -> dict[str, str]:
        snapshot = {}
        for path in sorted(root.rglob("*")):
            if path.is_file():
                rel = str(path.relative_to(root))
                if rel.endswith(".core-manifest.json"):
                    # Compare manifest with synced_at normalized (timestamp
                    # differs between runs — the acceptance criterion ignores it).
                    data = json.loads(path.read_text(encoding="utf-8"))
                    data.pop("synced_at", None)
                    snapshot[rel] = json.dumps(data, sort_keys=True)
                else:
                    snapshot[rel] = path.read_text(encoding="utf-8")
        return snapshot

    def test_library_and_cli_produce_identical_trees(self, tmp_path):
        src = build_source(tmp_path / "src")

        lib_target = tmp_path / "lib_target"
        lib_target.mkdir()
        sync(src, lib_target, SyncOptions(is_kit=True))

        cli_target = tmp_path / "cli_target"
        cli_target.mkdir()
        rc = main(["--source", str(src), "--target", str(cli_target), "--is-kit"])
        assert rc == 0

        assert self._tree_snapshot(lib_target) == self._tree_snapshot(cli_target)


# ── Self-sync: the engine upgrading itself ──────────────────────────────────
class TestSelfSync:
    """Production always hits this: the engine file is in scripts_core, so a
    sync overwrites the very ``sync_from_manifest.py`` that is executing.
    """

    def test_engine_upgrades_its_own_file(self, tmp_path):
        # Source is a real-ish tree whose engine file is a MODIFIED copy.
        src = build_source(tmp_path / "src")
        manifest = read_manifest(src)
        manifest["files"]["scripts_core"].append("core/sync_from_manifest.py")
        _write(
            src / "scripts" / ".core-manifest.json",
            json.dumps(manifest, indent=2),
        )
        modified_engine = "# MODIFIED ENGINE v2\n" + ENGINE.read_text(encoding="utf-8")
        _write(src / "scripts" / "core" / "sync_from_manifest.py", modified_engine)

        target = tmp_path / "target"
        target.mkdir()
        # Seed the target with the CURRENT engine so the sync overwrites it.
        _write(
            target / "scripts" / "core" / "sync_from_manifest.py",
            ENGINE.read_text(encoding="utf-8"),
        )

        report = sync(src, target, SyncOptions(is_kit=True))
        assert report.status in ("applied", "applied_with_warnings")
        synced = (target / "scripts" / "core" / "sync_from_manifest.py").read_text(
            encoding="utf-8"
        )
        assert synced == modified_engine


# ── Self-sync via a real subprocess (engine overwrites the running file) ────
class TestSelfSyncSubprocess:
    """Run the engine as a subprocess from the *target* copy, syncing a source
    whose engine file differs — proves overwriting the running file is safe.
    """

    def test_running_engine_overwrites_itself(self, tmp_path):
        src = build_source(tmp_path / "src")
        manifest = read_manifest(src)
        manifest["files"]["scripts_core"].append("core/sync_from_manifest.py")
        _write(
            src / "scripts" / ".core-manifest.json",
            json.dumps(manifest, indent=2),
        )
        modified_engine = "# MODIFIED ENGINE v2\n" + ENGINE.read_text(encoding="utf-8")
        _write(src / "scripts" / "core" / "sync_from_manifest.py", modified_engine)

        target = tmp_path / "target"
        (target / "scripts" / "core").mkdir(parents=True)
        running_engine = target / "scripts" / "core" / "sync_from_manifest.py"
        running_engine.write_text(ENGINE.read_text(encoding="utf-8"), encoding="utf-8")

        # Invoke the TARGET's engine copy against the source.
        result = subprocess.run(
            [
                sys.executable,
                str(running_engine),
                "--source",
                str(src),
                "--target",
                str(target),
                "--is-kit",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stderr
        assert running_engine.read_text(encoding="utf-8") == modified_engine
