"""Tests for `project sync` — the consumer-side core-sync pull wrapper (KIT-0036 D5).

Covers the `resolve_source` seam, is-kit inference, the branch/commit and
`--no-branch` mechanics, and the dual-*caller* contract: the engine's library
API and `project sync` produce identical trees (the third entrypoint that
completes the PR-1 dual-entrypoint test).
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CORE = REPO / "scripts" / "core"
sys.path.insert(0, str(CORE))  # for `import sync_from_manifest`

import sync_from_manifest  # noqa: E402

# Load the `project` script (no .py extension) as a module, mirroring
# test_project_script.py.
_project_path = CORE / "project"
_spec = importlib.util.spec_from_loader("project_cli", loader=None)
project_cli = importlib.util.module_from_spec(_spec)
with open(_project_path, encoding="utf-8") as _f:
    project_cli.__dict__["__file__"] = str(_project_path)
    exec(_f.read(), project_cli.__dict__)


# ── Fixtures ────────────────────────────────────────────────────────────────
def _write(path: Path, text: str, *, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if mode is not None:
        os.chmod(path, mode)


def build_kit(root: Path, *, opted_in: list[str] | None = None) -> Path:
    manifest = {
        "core_version": "9.9.0",
        "source_repo": "movito/test-kit",
        "synced_at": "2026-01-01T00:00:00Z",
        "files": {
            "scripts_core": ["core/foo.sh"],
            "commands_core": ["cmd.md"],
            "commands_optional": ["opt.md"],
            "kit_builder": [".kit/things/"],
        },
        "opted_in": opted_in or [],
    }
    _write(root / "scripts" / ".core-manifest.json", json.dumps(manifest, indent=2))
    _write(root / "scripts" / "core" / "foo.sh", "#!/bin/sh\necho foo\n", mode=0o755)
    _write(root / ".claude" / "commands" / "cmd.md", "# cmd\n")
    _write(root / ".claude" / "commands" / "opt.md", "# opt\n")
    _write(root / ".kit" / "things" / "a.md", "alpha\n")
    return root


def seed_consumer_manifest(root: Path, *, opted_in: list[str]) -> None:
    manifest = {
        "core_version": "0.0.0",
        "source_repo": "movito/test-kit",
        "synced_at": "2026-01-01T00:00:00Z",
        "files": {"scripts_core": [], "commands_core": []},
        "opted_in": opted_in,
    }
    _write(root / "scripts" / ".core-manifest.json", json.dumps(manifest, indent=2))


@pytest.fixture
def kit(tmp_path):
    return build_kit(tmp_path / "kit")


@pytest.fixture
def consumer(tmp_path):
    d = tmp_path / "consumer"
    d.mkdir()
    return d


# ── resolve_source / normalization ──────────────────────────────────────────
class TestResolveSource:
    def test_explicit_source_returned(self, kit, tmp_path):
        got = project_cli.resolve_source("main", str(kit), "x/y", tmp_path)
        assert (got / "scripts" / ".core-manifest.json").is_file()

    def test_nested_tarball_root_normalized(self, tmp_path):
        # Mimic a GitHub tarball: content nested one level under owner-repo-sha/.
        nested_parent = tmp_path / "extracted"
        build_kit(nested_parent / "movito-test-kit-abc1234")
        got = project_cli._normalize_source_root(nested_parent)
        assert (got / "scripts" / ".core-manifest.json").is_file()
        assert got.name == "movito-test-kit-abc1234"

    def test_missing_explicit_source_exits_4(self, tmp_path):
        with pytest.raises(SystemExit) as exc:
            project_cli.resolve_source("main", str(tmp_path / "nope"), "x/y", tmp_path)
        assert exc.value.code == 4


# ── is-kit inference ─────────────────────────────────────────────────────────
class TestIsKitInference:
    def test_kit_builder_opt_in_infers_kit(self, consumer):
        seed_consumer_manifest(consumer, opted_in=["kit_builder"])
        assert project_cli._infer_is_kit(consumer) is True

    def test_fresh_consumer_is_not_kit(self, consumer):
        assert project_cli._infer_is_kit(consumer) is False


# ── cmd_sync behavior ────────────────────────────────────────────────────────
class TestCmdSync:
    def test_dry_run_reports_drift_and_writes_nothing(self, kit, consumer):
        rc = project_cli.cmd_sync(["--source", str(kit), "--dry-run"], consumer)
        assert rc == 1  # drift
        assert not (consumer / "scripts" / "core" / "foo.sh").exists()

    def test_no_branch_applies_core_tiers(self, kit, consumer):
        rc = project_cli.cmd_sync(["--source", str(kit), "--no-branch"], consumer)
        assert rc == 0
        assert (consumer / "scripts" / "core" / "foo.sh").exists()
        assert (consumer / ".claude" / "commands" / "cmd.md").exists()
        # Fresh consumer is not a kit → builder tier and optional excluded.
        assert not (consumer / ".kit" / "things").exists()
        assert not (consumer / ".claude" / "commands" / "opt.md").exists()

    def test_is_kit_consumer_gets_builder_tier(self, kit, consumer):
        seed_consumer_manifest(consumer, opted_in=["kit_builder"])
        rc = project_cli.cmd_sync(["--source", str(kit), "--no-branch"], consumer)
        assert rc == 0
        assert (consumer / ".kit" / "things" / "a.md").exists()

    def test_unknown_flag_exit_2(self, kit, consumer):
        rc = project_cli.cmd_sync(["--source", str(kit), "--bogus"], consumer)
        assert rc == 2

    def test_missing_flag_value_exit_2(self, kit, consumer):
        assert project_cli.cmd_sync(["--source", str(kit), "--ref"], consumer) == 2
        # A flag as the next token is not a valid value either.
        assert (
            project_cli.cmd_sync(["--ref", "--dry-run", "--source", str(kit)], consumer)
            == 2
        )

    def test_missing_engine_returns_2_not_drift(self, kit, consumer, monkeypatch):
        # Setting a module to None in sys.modules makes `import` raise
        # ImportError — simulate a broken/partial install. Must NOT return 1
        # (drift), which automation would misread as "updates available".
        monkeypatch.setitem(sys.modules, "sync_from_manifest", None)
        rc = project_cli.cmd_sync(["--source", str(kit), "--dry-run"], consumer)
        assert rc == 2

    def test_exec_bit_preserved(self, kit, consumer):
        project_cli.cmd_sync(["--source", str(kit), "--no-branch"], consumer)
        import stat

        mode = stat.S_IMODE((consumer / "scripts" / "core" / "foo.sh").stat().st_mode)
        assert mode & 0o111


# ── Dual-caller contract: engine library API vs `project sync` ──────────────
class TestDualCallerContract:
    """The third entrypoint (`project sync`) must yield the same tree as the
    engine's library API for the same fixture (completes PR 1's dual-entrypoint
    test)."""

    def _snapshot(self, root: Path) -> dict[str, str]:
        snap = {}
        for path in sorted(root.rglob("*")):
            if path.is_file():
                rel = str(path.relative_to(root))
                if rel.endswith(".core-manifest.json"):
                    data = json.loads(path.read_text(encoding="utf-8"))
                    data.pop("synced_at", None)
                    snap[rel] = json.dumps(data, sort_keys=True)
                else:
                    snap[rel] = path.read_bytes().hex()
        return snap

    def test_project_sync_matches_library(self, tmp_path):
        import sync_from_manifest as engine

        kit = build_kit(tmp_path / "kit", opted_in=["kit_builder"])

        lib_target = tmp_path / "lib"
        lib_target.mkdir()
        seed_consumer_manifest(lib_target, opted_in=["kit_builder"])
        engine.sync(kit, lib_target, engine.SyncOptions(is_kit=True))

        cli_target = tmp_path / "cli"
        cli_target.mkdir()
        seed_consumer_manifest(cli_target, opted_in=["kit_builder"])
        rc = project_cli.cmd_sync(["--source", str(kit), "--no-branch"], cli_target)
        assert rc == 0

        assert self._snapshot(lib_target) == self._snapshot(cli_target)


# Run git with a sanitized env so ambient GIT_DIR/GIT_WORK_TREE (set e.g. by
# pre-commit while running the suite) can't redirect these tmp-repo operations
# onto the real repository.
def _git(*args, **kwargs):
    kwargs.setdefault("env", project_cli._clean_git_env())
    return subprocess.run(["git", *args], **kwargs)


# ── Branch + commit mechanics (default mode, needs a real git repo) ─────────
class TestBranchAndCommit:
    def _init_repo(self, root: Path) -> None:
        _git("init", "-q", str(root), check=True)
        _git("-C", str(root), "config", "user.email", "t@t", check=True)
        _git("-C", str(root), "config", "user.name", "t", check=True)
        _write(root / "README.md", "seed\n")
        _git("-C", str(root), "add", ".", check=True)
        _git("-C", str(root), "commit", "-qm", "seed", check=True)

    def test_default_mode_creates_branch_and_commits(self, kit, tmp_path):
        consumer = tmp_path / "consumer"
        consumer.mkdir()
        self._init_repo(consumer)

        rc = project_cli.cmd_sync(["--source", str(kit)], consumer)
        assert rc == 0

        branch = _git(
            "-C",
            str(consumer),
            "branch",
            "--show-current",
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        assert branch == "chore/core-sync-9.9.0"
        # The synced files were committed (clean tree after apply).
        status = _git(
            "-C",
            str(consumer),
            "status",
            "--porcelain",
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        assert status == ""
        assert (consumer / "scripts" / "core" / "foo.sh").exists()

    def test_no_branch_refuses_dirty_touched_path(self, kit, tmp_path):
        consumer = tmp_path / "consumer"
        consumer.mkdir()
        self._init_repo(consumer)
        # First sync so the file is tracked, then dirty it.
        project_cli.cmd_sync(["--source", str(kit), "--no-branch"], consumer)
        _git("-C", str(consumer), "add", ".", check=True)
        _git("-C", str(consumer), "commit", "-qm", "sync", check=True)
        (consumer / "scripts" / "core" / "foo.sh").write_text(
            "local edit\n", encoding="utf-8"
        )

        rc = project_cli.cmd_sync(["--source", str(kit), "--no-branch"], consumer)
        assert rc == 2  # refuses to overlay onto a dirty touched path

    def test_default_mode_does_not_sweep_unrelated_work(self, kit, tmp_path):
        consumer = tmp_path / "consumer"
        consumer.mkdir()
        self._init_repo(consumer)
        # Unrelated uncommitted file under a synced root — must NOT be committed.
        _write(consumer / "scripts" / "local" / "unrelated.txt", "my wip\n")

        rc = project_cli.cmd_sync(["--source", str(kit)], consumer)
        assert rc == 0

        tracked = _git(
            "-C",
            str(consumer),
            "ls-files",
            "scripts/local/unrelated.txt",
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        assert tracked == "", "unrelated file must not be swept into the sync commit"
        assert (consumer / "scripts" / "core" / "foo.sh").exists()

    def test_default_mode_also_refuses_dirty_touched_path(self, kit, tmp_path):
        # Branch mode must guard too — checkout -b would carry the dirty edit
        # onto the new branch where the engine would overwrite it.
        consumer = tmp_path / "consumer"
        consumer.mkdir()
        self._init_repo(consumer)
        project_cli.cmd_sync(["--source", str(kit), "--no-branch"], consumer)
        _git("-C", str(consumer), "add", ".", check=True)
        _git("-C", str(consumer), "commit", "-qm", "sync", check=True)
        (consumer / "scripts" / "core" / "foo.sh").write_text(
            "local edit\n", encoding="utf-8"
        )
        rc = project_cli.cmd_sync(["--source", str(kit)], consumer)  # default mode
        assert rc == 2

    def test_existing_sync_branch_is_uniquified_from_head(self, kit, tmp_path):
        # A second sync must create a FRESH branch from current HEAD, not switch
        # to the existing chore/core-sync-* tip (which would apply elsewhere).
        consumer = tmp_path / "consumer"
        consumer.mkdir()
        self._init_repo(consumer)
        base = _git(
            "-C",
            str(consumer),
            "branch",
            "--show-current",
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        project_cli.cmd_sync(["--source", str(kit)], consumer)  # chore/core-sync-9.9.0
        _git("-C", str(consumer), "checkout", "-q", base, check=True)

        project_cli.cmd_sync(["--source", str(kit)], consumer)  # must not reuse
        branch = _git(
            "-C",
            str(consumer),
            "branch",
            "--show-current",
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        assert branch == "chore/core-sync-9.9.0-2"

    def test_no_branch_refuses_dirty_manifest(self, kit, tmp_path):
        consumer = tmp_path / "consumer"
        consumer.mkdir()
        self._init_repo(consumer)
        project_cli.cmd_sync(["--source", str(kit), "--no-branch"], consumer)
        _git("-C", str(consumer), "add", ".", check=True)
        _git("-C", str(consumer), "commit", "-qm", "sync", check=True)
        # Uncommitted local manifest edit — the engine would overwrite it.
        (consumer / "scripts" / ".core-manifest.json").write_text(
            '{"core_version": "9.9.0", "files": {}, "opted_in": ["local-edit"]}\n',
            encoding="utf-8",
        )
        rc = project_cli.cmd_sync(["--source", str(kit), "--no-branch"], consumer)
        assert rc == 2  # dirty manifest trips the guard


KIT_MARKERS = REPO / "scripts" / "local" / "kit_markers.py"


def _shaped_root(tmp_path: Path, region: str, name: str = "shaped") -> Path:
    """A consumer root with a shape record (kit_markers + CLAUDE.md)."""
    root = tmp_path / name
    (root / "scripts" / "local").mkdir(parents=True)
    (root / "scripts" / "local" / "kit_markers.py").write_text(
        KIT_MARKERS.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (root / "CLAUDE.md").write_text(
        "# Repo\n\n<!-- BEGIN KIT-LOCAL: kit-install -->\n"
        f"{region}"
        "<!-- END KIT-LOCAL: kit-install -->\n",
        encoding="utf-8",
    )
    return root


def add_upstream_entry(kit: Path, tier: str, entry: str, relpath: str, body: str):
    """Add a brand-new upstream entry — the 'addition' a planning repo
    must skip and a single repo must receive."""
    manifest_path = kit / "scripts" / ".core-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"][tier].append(entry)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    _write(kit / relpath, body)


def seed_planning_manifest(root: Path) -> None:
    """The reduced manifest a planning bootstrap writes (KIT-0048)."""
    manifest = {
        "core_version": "1.0.0",
        "source_repo": "movito/test-kit",
        "synced_at": "2026-01-01T00:00:00Z",
        "files": {"scripts_core": ["core/foo.sh"], "commands_core": ["cmd.md"]},
        "opted_in": [],
    }
    _write(root / "scripts" / ".core-manifest.json", json.dumps(manifest, indent=2))


@pytest.mark.skipif(
    not KIT_MARKERS.exists(), reason="kit_markers.py absent (consumer checkout)"
)
class TestShapeScopedSync:
    """KIT-0049: planning repos sync by manifest intersection.

    Class-level skipif: pytest silently ignores marks on plain helper
    functions (claude-code review caught the decorator stranded on
    _shaped_root after the KIT-0048 class was replaced)."""

    @pytest.fixture
    def planning(self, tmp_path):
        root = _shaped_root(tmp_path, "shape: planning\n", name="planning")
        seed_planning_manifest(root)
        return root

    @pytest.fixture
    def kit_with_addition(self, tmp_path):
        kit = build_kit(tmp_path / "kit")
        add_upstream_entry(
            kit,
            "scripts_core",
            "core/extra.sh",
            "scripts/core/extra.sh",
            "#!/bin/sh\necho extra\n",
        )
        return kit

    def test_planning_sync_updates_only_recorded_files(
        self, kit_with_addition, planning
    ):
        rc = project_cli.cmd_sync(
            ["--source", str(kit_with_addition), "--no-branch"], planning
        )
        assert rc == 0
        assert (planning / "scripts" / "core" / "foo.sh").exists()
        assert (planning / ".claude" / "commands" / "cmd.md").exists()
        # the unrecorded addition must never appear
        assert not (planning / "scripts" / "core" / "extra.sh").exists()
        # opt-gated tiers stay out too (not recorded, not opted in)
        assert not (planning / ".claude" / "commands" / "opt.md").exists()

    def test_planning_sync_preserves_reduced_manifest(
        self, kit_with_addition, planning
    ):
        project_cli.cmd_sync(
            ["--source", str(kit_with_addition), "--no-branch"], planning
        )
        manifest = json.loads(
            (planning / "scripts" / ".core-manifest.json").read_text(encoding="utf-8")
        )
        # the reduced record survives — NOT upstream's full list
        assert manifest["files"] == {
            "scripts_core": ["core/foo.sh"],
            "commands_core": ["cmd.md"],
        }
        # everything recorded was synced: this run IS complete for this
        # shape — core_version converges, no partial flag
        assert manifest["core_version"] == "9.9.0"
        assert "partial_sync" not in manifest

    def test_planning_sync_names_skipped_additions(
        self, kit_with_addition, planning, capsys
    ):
        project_cli.cmd_sync(
            ["--source", str(kit_with_addition), "--no-branch"], planning
        )
        out = capsys.readouterr().out
        assert "core/extra.sh" in out
        assert "does not record" in out

    def test_single_shape_receives_additions_unchanged(
        self, kit_with_addition, tmp_path
    ):
        # characterization: a single-shape consumer still gets upstream
        # additions and the full upstream manifest
        consumer = tmp_path / "single-consumer"
        consumer.mkdir()
        rc = project_cli.cmd_sync(
            ["--source", str(kit_with_addition), "--no-branch"], consumer
        )
        assert rc == 0
        assert (consumer / "scripts" / "core" / "extra.sh").exists()
        manifest = json.loads(
            (consumer / "scripts" / ".core-manifest.json").read_text(encoding="utf-8")
        )
        assert "core/extra.sh" in manifest["files"]["scripts_core"]

    def test_malformed_shape_still_refused(self, tmp_path):
        root = _shaped_root(tmp_path, "shape: pyramid\n")
        rc = project_cli.cmd_sync(["--dry-run"], root)
        assert rc == 2

    def test_planning_without_manifest_refused(self, kit_with_addition, tmp_path):
        root = _shaped_root(tmp_path, "shape: planning\n")
        rc = project_cli.cmd_sync(
            ["--source", str(kit_with_addition), "--dry-run"], root
        )
        assert rc == 2

    def test_single_shape_not_blocked_by_guard(self, tmp_path, capsys):
        root = _shaped_root(tmp_path, "shape: single\n")
        rc = project_cli.cmd_sync(["--dry-run"], root)
        # proceeds past the guard (fails later for engine reasons, but
        # never with the shape-refusal message)
        captured = capsys.readouterr()
        assert "sync refused" not in captured.out
        assert rc != 2 or "KIT-0049" not in captured.out

    def test_upstream_deletion_pruned_from_preserved_manifest(
        self, kit_with_addition, planning, capsys
    ):
        """o3 review: an upstream-dropped entry must be pruned from the
        preserved manifest, not frozen into a stale record forever."""
        manifest_path = kit_with_addition / "scripts" / ".core-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"]["commands_core"].remove("cmd.md")
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        (kit_with_addition / ".claude" / "commands" / "cmd.md").unlink()

        rc = project_cli.cmd_sync(
            ["--source", str(kit_with_addition), "--no-branch"], planning
        )
        assert rc == 0
        result = json.loads(
            (planning / "scripts" / ".core-manifest.json").read_text(encoding="utf-8")
        )
        # pruned from the record; announced in the output
        assert result["files"]["commands_core"] == []
        assert result["files"]["scripts_core"] == ["core/foo.sh"]
        assert "cmd.md" in capsys.readouterr().out

    def test_only_outside_allowlist_is_usage_error(self, kit_with_addition, planning):
        """o3 review: an explicit --only request outside the allowlist
        must refuse (exit 2), never silently become a skipped addition."""
        rc = project_cli.cmd_sync(
            [
                "--source",
                str(kit_with_addition),
                "--no-branch",
                "--only",
                "core/extra.sh",
            ],
            planning,
        )
        assert rc == 2

    def test_null_files_section_refused_not_crash(self, kit_with_addition, tmp_path):
        """fast-v2 review: "files": null raised AttributeError past the
        except tuple — must refuse with exit 2 instead."""
        root = _shaped_root(tmp_path, "shape: planning\n", name="nullfiles")
        _write(
            root / "scripts" / ".core-manifest.json",
            json.dumps({"core_version": "1.0.0", "files": None}),
        )
        rc = project_cli.cmd_sync(
            ["--source", str(kit_with_addition), "--dry-run"], root
        )
        assert rc == 2

    def test_string_tier_refused_not_char_iterated(self, kit_with_addition, tmp_path):
        """BugBot PR #79: a string-valued tier iterates as characters,
        silently poisoning the allowlist — must refuse (exit 2)."""
        root = _shaped_root(tmp_path, "shape: planning\n", name="strtier")
        _write(
            root / "scripts" / ".core-manifest.json",
            json.dumps(
                {"core_version": "1.0.0", "files": {"scripts_core": "core/foo.sh"}}
            ),
        )
        rc = project_cli.cmd_sync(
            ["--source", str(kit_with_addition), "--dry-run"], root
        )
        assert rc == 2

    def test_traversal_entry_in_manifest_refused(
        self, kit_with_addition, tmp_path, capsys
    ):
        """claude-code review: consumer-manifest entries get the same
        path rules as the source manifest (defense in depth)."""
        root = _shaped_root(tmp_path, "shape: planning\n", name="traversal")
        _write(
            root / "scripts" / ".core-manifest.json",
            json.dumps(
                {
                    "core_version": "1.0.0",
                    "files": {"scripts_core": ["core/foo.sh", "../../evil"]},
                }
            ),
        )
        rc = project_cli.cmd_sync(
            ["--source", str(kit_with_addition), "--dry-run"], root
        )
        assert rc == 2
        assert "unsafe path" in capsys.readouterr().out

    def test_engine_allowlist_report_fields(self, kit_with_addition, tmp_path):
        # engine-level: skipped additions land in the report, sorted;
        # allowlist runs count as complete for their scope
        target = tmp_path / "engine-target"
        target.mkdir()
        seed_planning_manifest(target)
        report = sync_from_manifest.sync(
            kit_with_addition,
            target,
            sync_from_manifest.SyncOptions(allowlist=["core/foo.sh", "cmd.md"]),
        )
        assert report.skipped_additions == ["core/extra.sh"]
        assert report.complete is True
        assert report.to_dict()["skipped_additions"] == ["core/extra.sh"]
