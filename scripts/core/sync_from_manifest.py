#!/usr/bin/env python3
"""Manifest-driven sync engine — one engine, two callers (KIT-ADR-0026).

This module is the single implementation of Channel B's sync contract. Both
the push Action (``.github/workflows/sync-core-scripts.yml``) and the
consumer-side pull wrapper (``project sync``) invoke it, so the two paths
cannot drift: there is nothing to drift from.

Design invariants (see KIT-ADR-0026 and KIT-0036 for the full rationale):

* **Library-first, CLI-thin.** :func:`sync` is the importable entry point and
  returns a :class:`SyncReport`; the ``__main__`` block is a thin argparse
  layer that maps ``SyncReport.status`` to the exit-code contract below.
* **Full plan in memory before the first write.** Every read of the *source*
  tree (file bytes *and* permission bits) and both manifests happens during
  the plan phase. The apply phase writes only from memory, so the engine
  overwriting *itself* mid-run (its own file lives in ``scripts_core``) is a
  non-issue — nothing is re-read from disk once writing starts.
* **Two-pass temp-then-commit (KIT-0034 F3).** Every file/directory operation
  is staged into a temp tree first; only after the whole plan is staged does
  the commit pass move things into the target. A failed sync never leaves a
  half-updated consumer.
* **Engine-computed completeness.** The engine — not the caller — decides
  whether a run is a full sync by comparing the effective sync set against the
  target's full entitlement. A complete sync bumps ``core_version`` and clears
  ``partial_sync``; a partial one leaves ``core_version`` and sets
  ``partial_sync: true``.

Exit-code contract (frozen by tests, documented in ``--help``):

* ``0`` — clean (no drift) or changes applied without warnings.
* ``1`` — drift found (``--dry-run``) **or** changes applied with warnings.
  These are deliberately conflated: both mean *a human should look*. Machine
  consumers needing finer discrimination read ``--report-json``, whose
  ``status`` field distinguishes ``drift`` from ``applied_with_warnings``.
* ``2`` — usage error (unknown ``--tier``/``--only`` key, non-entitled tier).
* ``3`` — source manifest missing/unrecognized, or the target manifest exists
  but is corrupt (refusing to sync would silently reset ``opted_in``).
* ``4`` — source tree unreadable.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# ── Exit-code contract ──────────────────────────────────────────────────────
EXIT_OK = 0
EXIT_ATTENTION = 1
EXIT_USAGE = 2
EXIT_MANIFEST = 3
EXIT_SOURCE = 4

# SyncReport.status → process exit code. Only the four "ran to completion"
# statuses live here; the typed exceptions below carry the 2/3/4 codes.
STATUS_EXIT = {
    "clean": EXIT_OK,
    "applied": EXIT_OK,
    "drift": EXIT_ATTENTION,
    "applied_with_warnings": EXIT_ATTENTION,
}

MANIFEST_RELPATH = "scripts/.core-manifest.json"
REQUIRED_MANIFEST_KEYS = {"core_version", "files"}


# ── Typed errors (each maps to a distinct exit code) ────────────────────────
class SyncError(Exception):
    """Base class for engine errors that map to a specific exit code."""

    exit_code = EXIT_ATTENTION


class UsageError(SyncError):
    """Bad caller input: unknown tier/entry key, non-entitled tier."""

    exit_code = EXIT_USAGE


class ManifestError(SyncError):
    """Source manifest missing or its schema is unrecognized."""

    exit_code = EXIT_MANIFEST


class SourceError(SyncError):
    """Source tree cannot be read."""

    exit_code = EXIT_SOURCE


# ── Data model ──────────────────────────────────────────────────────────────
@dataclass
class SyncOptions:
    """Narrowing and mode flags for a single :func:`sync` invocation."""

    tiers: list[str] | None = None
    only: list[str] | None = None
    dry_run: bool = False
    is_kit: bool = False


@dataclass
class SyncReport:
    """Outcome of a :func:`sync` run — the contract callers branch on.

    Callers branch their UX on :attr:`status` (not the exit code, which
    conflates ``drift`` and ``applied_with_warnings``).
    """

    status: str
    dry_run: bool
    complete: bool
    synced_tiers: list[str] = field(default_factory=list)
    added: list[str] = field(default_factory=list)
    modified: list[str] = field(default_factory=list)
    removed_files: list[str] = field(default_factory=list)
    removed_entries: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    would_bump_core_version: bool = False
    would_set_partial_sync: bool = False
    core_version: str = ""

    @property
    def exit_code(self) -> int:
        return STATUS_EXIT[self.status]

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "exit_code": self.exit_code,
            "dry_run": self.dry_run,
            "complete": self.complete,
            "synced_tiers": self.synced_tiers,
            "added": self.added,
            "modified": self.modified,
            "removed_files": self.removed_files,
            "removed_entries": self.removed_entries,
            "warnings": self.warnings,
            "would_bump_core_version": self.would_bump_core_version,
            "would_set_partial_sync": self.would_set_partial_sync,
            "core_version": self.core_version,
        }


# A single planned file: its bytes and permission bits, captured up front.
@dataclass
class _FileContent:
    data: bytes
    mode: int


# A planned operation against one manifest entry.
@dataclass
class _Op:
    kind: str  # "file" or "dir"
    relpath: str  # path relative to the repo root (source and target share it)
    # For "file": a single _FileContent under `file`.
    # For "dir": a mapping of {path-relative-to-dir: _FileContent}.
    file: _FileContent | None = None
    dir_files: dict[str, _FileContent] = field(default_factory=dict)


# ── Manifest helpers ────────────────────────────────────────────────────────
def _read_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_source_manifest(source_root: Path) -> dict:
    """Load and validate the *source* manifest. Raises on any problem.

    The engine's contract is with the manifest *schema*, not the source's
    engine version: an unrecognized shape (missing keys, legacy flat-array
    ``files``) is a loud failure (exit 3), never a guess.
    """
    manifest_path = source_root / MANIFEST_RELPATH
    if not manifest_path.is_file():
        raise ManifestError(f"source manifest not found: {manifest_path}")
    try:
        data = _read_json(manifest_path)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ManifestError(f"source manifest is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ManifestError("source manifest must be a JSON object")
    missing = REQUIRED_MANIFEST_KEYS - set(data.keys())
    if missing:
        raise ManifestError(
            f"source manifest missing required key(s): {', '.join(sorted(missing))}"
        )
    if not isinstance(data["files"], dict):
        raise ManifestError(
            "source manifest 'files' must be a tier→entries object "
            "(legacy flat-array manifests predate this engine)"
        )
    return data


def _read_target_manifest(target_root: Path) -> dict | None:
    """Read the target manifest. Absent → fresh consumer; corrupt → loud fail.

    A missing manifest means a genuinely fresh consumer (returns ``None``). A
    manifest that *exists* but cannot be parsed as a JSON object is a loud
    failure (:class:`ManifestError`, exit 3): treating it as fresh would
    silently reset the consumer's ``opted_in`` list and drop their opt-ins.
    An older-but-valid dict schema is still read leniently.
    """
    manifest_path = target_root / MANIFEST_RELPATH
    if not manifest_path.is_file():
        return None
    try:
        data = _read_json(manifest_path)
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        raise ManifestError(
            f"target manifest exists but is unreadable: {manifest_path} ({exc}). "
            "Fix or remove it — refusing to sync and silently reset opted_in."
        ) from exc
    if not isinstance(data, dict):
        raise ManifestError(
            f"target manifest is not a JSON object: {manifest_path}. "
            "Fix or remove it — refusing to sync and silently reset opted_in."
        )
    return data


def _all_entries(files_section: object) -> set[str]:
    """All entry keys in a manifest ``files`` section (dict or legacy list)."""
    if isinstance(files_section, dict):
        return {entry for entries in files_section.values() for entry in entries}
    if isinstance(files_section, list):
        return set(files_section)
    return set()


def should_sync_tier(tier: str, is_kit: bool, opted_in: list[str]) -> bool:
    """Tier entitlement rule, ported verbatim from the workflow heredoc.

    Core tiers (``*_core``) always sync; ``kit_builder`` syncs only to kit
    repos (``is_kit``); every other tier syncs only if the target opted in.
    """
    if tier.endswith("_core"):
        return True
    if tier == "kit_builder":
        return is_kit
    return tier in opted_in


def _rel_path(tier: str, entry: str) -> str:
    """Map a (tier, entry) pair to a path relative to the repo root.

    Both source and target share this layout, so the same relpath resolves
    under either root. Ported from the workflow's ``resolve_paths``.
    """
    if tier == "scripts_core":
        return f"scripts/{entry}"
    if tier.startswith("commands_"):
        return f".claude/commands/{entry}"
    return entry


# ── Filesystem helpers (plan reads; apply writes) ───────────────────────────
def _read_file(path: Path) -> _FileContent:
    return _FileContent(data=path.read_bytes(), mode=stat.S_IMODE(path.stat().st_mode))


def _read_dir(path: Path) -> dict[str, _FileContent]:
    """Read every file under ``path`` into memory, keyed by relative path."""
    contents: dict[str, _FileContent] = {}
    for child in sorted(path.rglob("*")):
        if child.is_file():
            contents[str(child.relative_to(path))] = _read_file(child)
    return contents


def _write_file(path: Path, content: _FileContent) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.data)
    os.chmod(path, content.mode)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Planning ────────────────────────────────────────────────────────────────
def _select_tiers(
    upstream_files: dict,
    entitled_tiers: list[str],
    requested: list[str] | None,
) -> list[str]:
    """Resolve which tiers to sync, validating any explicit ``--tier`` request."""
    if not requested:
        return entitled_tiers
    entitled_set = set(entitled_tiers)
    known = set(upstream_files.keys())
    selected: list[str] = []
    for tier in requested:
        if tier not in known:
            raise UsageError(
                f"unknown tier {tier!r}. known tiers: " f"{', '.join(sorted(known))}"
            )
        if tier not in entitled_set:
            raise UsageError(
                f"tier {tier!r} is not entitled for this target "
                "(not a core tier, not opted in, or requires --is-kit). "
                "add it to the manifest 'opted_in' array or pass --is-kit."
            )
        selected.append(tier)
    return selected


def _apply_only_filter(
    candidates: list[tuple[str, str]],
    upstream_files: dict,
    only: list[str] | None,
) -> list[tuple[str, str]]:
    """Filter (tier, entry) candidates to an explicit ``--only`` entry set.

    ``--only`` takes a manifest entry key exactly as it appears in the JSON
    (directory entries keep their trailing slash). An unknown key is a usage
    error whose message surfaces the near-miss (e.g. a missing trailing slash).
    """
    if not only:
        return candidates
    all_entries = _all_entries(upstream_files)
    selectable = {entry for _tier, entry in candidates}
    for key in only:
        if key in all_entries:
            continue
        hint = ""
        near = f"{key}/"
        near_stripped = key.rstrip("/")
        if near in all_entries:
            hint = f" (did you mean {near!r}? directory entries keep the slash)"
        elif near_stripped in all_entries:
            hint = f" (did you mean {near_stripped!r}? that entry is a file)"
        raise UsageError(f"--only entry {key!r} is not in the manifest{hint}")
    # Keys that exist in the manifest but are outside the entitled/selected
    # tiers are a usage error too — the caller asked for something the target
    # is not entitled to (or excluded via --tier).
    unreachable = [k for k in only if k in all_entries and k not in selectable]
    if unreachable:
        raise UsageError(
            "--only entr(y/ies) not reachable in the selected tiers: "
            f"{', '.join(sorted(unreachable))} "
            "(the entry's tier is not entitled or was excluded by --tier)"
        )
    only_set = set(only)
    return [(tier, entry) for tier, entry in candidates if entry in only_set]


def _build_plan(
    source_root: Path,
    candidates: list[tuple[str, str]],
) -> tuple[list[_Op], list[str]]:
    """Read all source content for the selected entries into memory.

    Returns the ordered plan plus any warnings about missing source paths.
    This is the *only* phase that reads the source tree.
    """
    plan: list[_Op] = []
    warnings: list[str] = []
    for tier, entry in candidates:
        relpath = _rel_path(tier, entry)
        src = source_root / relpath
        if entry.endswith("/"):
            if not src.is_dir():
                warnings.append(f"source directory not found: {relpath}")
                continue
            plan.append(
                _Op(
                    kind="dir",
                    relpath=relpath.removesuffix("/"),
                    dir_files=_read_dir(src),
                )
            )
        else:
            if not src.is_file():
                warnings.append(f"source file not found: {relpath}")
                continue
            plan.append(_Op(kind="file", relpath=relpath, file=_read_file(src)))
    return plan, warnings


def _diff_plan(
    plan: list[_Op],
    target_root: Path,
    target_manifest: dict | None,
    target_old_entries: set[str],
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Compare the planned end-state against the current target tree.

    Returns (added, modified, removed_files, overwrite_warnings). ``removed_files``
    are files that exist under a directory entry downstream but not upstream —
    the stale-file cleanup that directory replacement performs.
    """
    added: list[str] = []
    modified: list[str] = []
    removed_files: list[str] = []
    warnings: list[str] = []
    for op in plan:
        if op.kind == "file":
            tgt = target_root / op.relpath
            if not tgt.exists():
                added.append(op.relpath)
            else:
                # Compare bytes AND mode: _apply reapplies mode via os.chmod,
                # so a file that only lost its executable bit is real drift.
                current = _read_file(tgt)
                if current.data != op.file.data or current.mode != op.file.mode:
                    modified.append(op.relpath)
            # Overwrite warning: a manifest exists, the file is present, and it
            # was never a tracked manifest entry — the consumer is about to lose
            # a local file the sync unit did not previously own.
            if target_manifest is not None and tgt.exists():
                key = _entry_key_for_relpath(op.relpath)
                if key is not None and key not in target_old_entries:
                    warnings.append(
                        f"Overwriting '{key}' which was not previously in the manifest"
                    )
        else:  # dir
            tgt_dir = target_root / op.relpath
            existing = _read_dir(tgt_dir) if tgt_dir.is_dir() else {}
            for rel, content in op.dir_files.items():
                full = f"{op.relpath}/{rel}"
                if rel not in existing:
                    added.append(full)
                elif (
                    existing[rel].data != content.data
                    or existing[rel].mode != content.mode
                ):
                    modified.append(full)
            for rel in existing:
                if rel not in op.dir_files:
                    removed_files.append(f"{op.relpath}/{rel}")
    return added, modified, removed_files, warnings


def _entry_key_for_relpath(relpath: str) -> str | None:
    """Recover the manifest entry key from a repo-relative path.

    Inverse of :func:`_rel_path` for file entries — used for the
    not-previously-in-manifest overwrite warning.
    """
    if relpath.startswith("scripts/"):
        return relpath[len("scripts/") :]
    if relpath.startswith(".claude/commands/"):
        return relpath[len(".claude/commands/") :]
    return relpath


# ── Manifest construction ───────────────────────────────────────────────────
def _build_new_manifest(
    upstream: dict,
    target_manifest: dict | None,
    complete: bool,
) -> dict:
    """Build the manifest to write to the target.

    Takes the upstream ``files``/``source_repo`` (the sync contract), preserves
    the target's ``opted_in`` verbatim, and sets metadata per completeness.
    """
    new_manifest = json.loads(json.dumps(upstream))  # deep copy, key order kept

    if target_manifest is not None and isinstance(
        target_manifest.get("opted_in"), list
    ):
        new_manifest["opted_in"] = target_manifest["opted_in"]
    else:
        # Fresh consumer: opt into nothing (matches the workflow's [] default).
        new_manifest["opted_in"] = []

    target_core_version = (
        target_manifest.get("core_version") if target_manifest else None
    )
    if complete:
        new_manifest["core_version"] = upstream["core_version"]
        new_manifest.pop("partial_sync", None)
    else:
        # Leave core_version untouched for a partial sync; a fresh consumer has
        # no prior version, so fall back to upstream's but flag the mixed tree.
        if target_core_version is not None:
            new_manifest["core_version"] = target_core_version
        else:
            new_manifest["core_version"] = upstream["core_version"]
        new_manifest["partial_sync"] = True

    new_manifest["synced_at"] = _utcnow_iso()
    return new_manifest


def _manifest_without_synced_at(manifest: dict | None) -> dict:
    if not manifest:
        return {}
    clone = dict(manifest)
    clone.pop("synced_at", None)
    return clone


# ── Apply (two-pass temp-then-commit) ───────────────────────────────────────
def _apply(
    plan: list[_Op],
    new_manifest: dict,
    target_root: Path,
) -> None:
    """Stage the whole plan into a temp tree, then commit it with moves only.

    The staging directory is created *inside* the target root so that the
    commit-pass moves are same-filesystem renames. Nothing reads the source
    here — every byte comes from the in-memory plan.
    """
    target_root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".core-sync-", dir=target_root))
    try:
        # ── Pass 1: stage everything ──
        staged: list[tuple[str, Path, Path]] = []  # (kind, staged_path, final_path)
        for op in plan:
            if op.kind == "file":
                staged_path = staging / op.relpath
                _write_file(staged_path, op.file)
                staged.append(("file", staged_path, target_root / op.relpath))
            else:
                staged_dir = staging / op.relpath
                for rel, content in op.dir_files.items():
                    _write_file(staged_dir / rel, content)
                staged_dir.mkdir(parents=True, exist_ok=True)
                staged.append(("dir", staged_dir, target_root / op.relpath))

        manifest_bytes = (
            json.dumps(new_manifest, indent=2, ensure_ascii=False) + "\n"
        ).encode("utf-8")
        staged_manifest = staging / MANIFEST_RELPATH
        _write_file(staged_manifest, _FileContent(data=manifest_bytes, mode=0o644))

        # ── Pass 2: commit (moves only — no source reads, no re-staging) ──
        for kind, staged_path, final_path in staged:
            if kind == "file":
                final_path.parent.mkdir(parents=True, exist_ok=True)
                os.replace(staged_path, final_path)
            else:
                if final_path.exists():
                    shutil.rmtree(final_path)
                final_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(staged_path), str(final_path))
        (target_root / MANIFEST_RELPATH).parent.mkdir(parents=True, exist_ok=True)
        os.replace(staged_manifest, target_root / MANIFEST_RELPATH)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


# ── Public entry point ──────────────────────────────────────────────────────
def sync(source: str | Path, target: str | Path, options: SyncOptions) -> SyncReport:
    """Sync ``source`` → ``target`` per the manifest and ``options``.

    Returns a :class:`SyncReport`. Raises :class:`SourceError` (exit 4),
    :class:`ManifestError` (exit 3), or :class:`UsageError` (exit 2) for the
    corresponding failure classes; the CLI maps these to process exit codes.
    """
    source_root = Path(source)
    target_root = Path(target)

    if not source_root.is_dir():
        raise SourceError(f"source tree not readable: {source_root}")

    upstream = load_source_manifest(source_root)
    target_manifest = _read_target_manifest(target_root)

    target_opted_in: list[str] = []
    if target_manifest is not None and isinstance(
        target_manifest.get("opted_in"), list
    ):
        target_opted_in = target_manifest["opted_in"]
    target_old_entries = _all_entries(
        target_manifest.get("files") if target_manifest else None
    )

    upstream_files: dict = upstream["files"]

    # ── Entitlement and selection ──
    entitled_tiers = [
        tier
        for tier in upstream_files
        if should_sync_tier(tier, options.is_kit, target_opted_in)
    ]
    full_entitlement = {
        entry for tier in entitled_tiers for entry in upstream_files[tier]
    }

    selected_tiers = _select_tiers(upstream_files, entitled_tiers, options.tiers)
    candidates = [
        (tier, entry) for tier in selected_tiers for entry in upstream_files[tier]
    ]
    candidates = _apply_only_filter(candidates, upstream_files, options.only)

    effective_entries = {entry for _tier, entry in candidates}
    complete = effective_entries == full_entitlement

    # ── Plan (only source-reading phase) ──
    plan, plan_warnings = _build_plan(source_root, candidates)
    added, modified, removed_files, overwrite_warnings = _diff_plan(
        plan, target_root, target_manifest, target_old_entries
    )
    warnings = overwrite_warnings + plan_warnings

    # ── Manifest-level removals (entries dropped from the sync unit) ──
    upstream_all_entries = _all_entries(upstream_files)
    removed_entries = sorted(target_old_entries - upstream_all_entries)

    new_manifest = _build_new_manifest(upstream, target_manifest, complete)
    new_core_version = new_manifest["core_version"]

    would_bump = complete and (
        target_manifest is None
        or target_manifest.get("core_version") != upstream["core_version"]
    )
    would_set_partial = not complete

    content_changed = bool(added or modified or removed_files or removed_entries)
    manifest_changed = _manifest_without_synced_at(
        new_manifest
    ) != _manifest_without_synced_at(target_manifest)
    should_write = content_changed or manifest_changed

    synced_tiers = sorted({tier for tier, _entry in candidates})

    # ── Status determination ──
    if options.dry_run:
        # Drift mirrors what a real run would write: file content changes OR a
        # manifest metadata change (core_version bump, partial_sync clear) that
        # a non-dry run would persist. synced_at alone never counts as drift.
        status = "drift" if should_write else "clean"
    else:
        if should_write:
            _apply(plan, new_manifest, target_root)
        if warnings:
            status = "applied_with_warnings"
        elif content_changed:
            status = "applied"
        else:
            status = "clean"

    return SyncReport(
        status=status,
        dry_run=options.dry_run,
        complete=complete,
        synced_tiers=synced_tiers,
        added=sorted(added),
        modified=sorted(modified),
        removed_files=sorted(removed_files),
        removed_entries=removed_entries,
        warnings=warnings,
        would_bump_core_version=would_bump,
        would_set_partial_sync=would_set_partial,
        core_version=new_core_version,
    )


# ── CLI ─────────────────────────────────────────────────────────────────────
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sync_from_manifest.py",
        description=(
            "Manifest-driven sync engine (KIT-ADR-0026). Syncs core scripts, "
            "commands, and builder-layer files from a source tree into a "
            "target tree according to scripts/.core-manifest.json."
        ),
        epilog=(
            "Exit codes: 0 clean/applied; 1 drift (--dry-run) or applied with "
            "warnings (both mean a human should look — read --report-json to "
            "distinguish); 2 usage error; 3 source manifest missing/"
            "unrecognized or target manifest corrupt; 4 source unreadable."
        ),
    )
    parser.add_argument("--source", required=True, help="source (upstream) tree root")
    parser.add_argument("--target", required=True, help="target (consumer) tree root")
    parser.add_argument(
        "--tier",
        action="append",
        dest="tiers",
        metavar="TIER",
        help="restrict to this tier (repeatable); default is every entitled tier",
    )
    parser.add_argument(
        "--only",
        action="append",
        dest="only",
        metavar="ENTRY",
        help=(
            "restrict to this manifest entry key, exactly as it appears in the "
            "manifest (directory entries keep the trailing slash); repeatable"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report what would change without writing anything",
    )
    parser.add_argument(
        "--is-kit",
        action="store_true",
        help="treat the target as a kit repo (syncs the kit_builder tier)",
    )
    parser.add_argument(
        "--report-json",
        metavar="FILE",
        help="write the full SyncReport as JSON to FILE",
    )
    return parser


def _print_report(report: SyncReport) -> None:
    """Human-readable summary to stderr (stdout stays clean for piping)."""
    if report.dry_run:
        header = "would change" if report.status == "drift" else "up to date"
        print(f"[dry-run] {header}", file=sys.stderr)
    else:
        print(f"sync {report.status}", file=sys.stderr)
    for label, items in (
        ("added", report.added),
        ("modified", report.modified),
        ("removed (in directory entries)", report.removed_files),
        ("removed from sync unit", report.removed_entries),
    ):
        for item in items:
            print(f"  {label}: {item}", file=sys.stderr)
    for warning in report.warnings:
        print(f"  warning: {warning}", file=sys.stderr)
    if report.would_set_partial_sync:
        print("  note: partial sync — core_version left unchanged", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    options = SyncOptions(
        tiers=args.tiers,
        only=args.only,
        dry_run=args.dry_run,
        is_kit=args.is_kit,
    )
    try:
        report = sync(args.source, args.target, options)
    except SyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code

    if args.report_json:
        with open(args.report_json, "w", encoding="utf-8") as handle:
            json.dump(report.to_dict(), handle, indent=2, ensure_ascii=False)
            handle.write("\n")

    _print_report(report)
    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
