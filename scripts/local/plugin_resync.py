#!/usr/bin/env python3
"""Plugin resync tool (KIT-0110): codify the release resync method.

Three releases (2.0.2 → 2.0.4) ran this method as hand-rolled ``/tmp``
tooling — the kit's own third-occurrence rule. What it does, per shipped
component in ``plugins/agentive-workflow/roster.yaml``:

1. **Work-list from roster hashes, never ``git diff``** (KIT-0099): a
   component is drifted when the sha256 of its kit source file no longer
   matches the rostered ``kit_sha256``.
2. **Three-way merge, never copy** (KIT-0109): base = the kit file's
   content at the previously-rostered hash, theirs = the kit working
   tree, ours = the published plugin body. A straight copy would flatten
   the KIT-ADR-0025 generalization the plugin bodies legitimately carry.
   ``kit_sha256`` is a CONTENT hash, not a git blob id — the base is
   found by walking the kit file's history and hashing each version
   until it matches (``find_base_content``). No historical match is a
   loud per-component failure (exit 3), never a silent copy.
3. **Conflicts are surfaced, not solved**: a conflicting merge leaves
   the published body untouched and writes the conflict-marked result
   next to it as ``<body>.conflict`` for the human (exit 1).
4. **Roster maintenance**: cleanly resynced entries get their
   ``kit_sha256`` (and ``kit_version``, from the kit file's frontmatter)
   refreshed, and every shipped entry gets ``plugin_sha256`` — the hash
   of the published body — recomputed. That column is what the
   marketplace-side CI check verifies (the drift guard's blind half;
   see the division-of-verification note in ``check_plugin_drift.py``).

Modes: default = full resync; ``--dry-run`` emits the work-list only;
``--hashes-only`` skips all body writes and only refreshes the
``plugin_sha256`` column (used to populate the column without touching
content).

Kit-internal: lives in ``scripts/local/`` and is NOT synced to consumer
projects. Both repos are local checkouts — no network. Exit codes follow
the kit convention: ``0`` success, ``1`` conflicts surfaced, ``2``
usage/environment error, ``3`` integrity error (base not found, or a
published body missing in ``--hashes-only`` mode), ``4`` roster
read/parse error.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Reuse the drift guard's roster parser (same schema, same validation) so
# the resync tool and the guard can never disagree about what a valid
# roster is (KIT-0110 evaluator F3).
_GUARD_PATH = Path(__file__).resolve().parent / "check_plugin_drift.py"
_spec = importlib.util.spec_from_file_location("check_plugin_drift", _GUARD_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError(f"cannot load the drift guard from {_GUARD_PATH}")
_guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_guard)

PLUGIN_REL = "plugins/agentive-workflow"
ROSTER_REL = f"{PLUGIN_REL}/roster.yaml"

# Component names become file paths under the plugin tree; refuse anything
# that could traverse (the roster is data, not trusted input). No leading
# dot: a hidden shipped file is never a legitimate component (KIT-0110
# evaluator; same rule as the marketplace-side verify script).
_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

EXIT_OK = 0
EXIT_CONFLICTS = 1
EXIT_USAGE = 2
EXIT_INTEGRITY = 3
EXIT_ROSTER_IO = 4


class ResyncError(Exception):
    """A per-component or environment failure worth naming loudly."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
        )
    except FileNotFoundError as exc:
        raise ResyncError("git is not on PATH — the resync needs it") from exc


def plugin_body_relpath(comp: dict) -> str:
    """Relative path (under the plugin dir) of a component's shipped body."""
    kind = comp.get("kind")
    name = comp["name"]
    if kind == "agent":
        return f"agents/{name}.md"
    if kind == "command":
        return f"commands/{name}.md"
    if kind == "skill":
        return f"skills/{name}/SKILL.md"
    raise ResyncError(f"{name}: unknown kind {kind!r} — cannot derive body path")


def validate_shipped(components: list[dict]) -> None:
    """Resync-specific validation on top of the guard's schema checks.

    The guard validates names/sources/hashes generically; the resync tool
    additionally derives filesystem paths from ``kind`` + ``name``, so
    both must be safe before any path is built.
    """
    problems: list[str] = []
    for comp in components:
        if not comp.get("ships", False):
            continue
        name = comp.get("name", "<unnamed>")
        if not _SAFE_NAME.match(name):
            problems.append(f"{name!r}: unsafe component name for path use")
        if comp.get("kind") not in ("agent", "command", "skill"):
            problems.append(f"{name}: unknown kind {comp.get('kind')!r}")
    if problems:
        print("ERROR: roster records unusable for resync:")
        for p in problems:
            print(f"  - {p}")
        raise SystemExit(EXIT_ROSTER_IO)


def find_base_content(kit_root: Path, source: str, want_sha256: str) -> bytes | None:
    """Return the historical kit content whose sha256 matches the roster.

    ``kit_sha256`` is a content hash, not a git blob id, so the base is
    found by walking the file's history (``git log --format=%H --
    <path>``) and hashing each version (``git show <rev>:<path>``) until
    one matches. Returns None when no historical version matches — the
    caller must fail loud, never fall back to a copy.
    """
    proc = _git(kit_root, "log", "--format=%H", "--", source)
    if proc.returncode != 0:
        raise ResyncError(
            f"git log failed for {source} in {kit_root}: "
            f"{proc.stderr.decode('utf-8', 'replace').strip()}"
        )
    for rev in proc.stdout.decode("utf-8").split():
        shown = _git(kit_root, "show", f"{rev}:{source}")
        if shown.returncode != 0:
            continue  # path absent at this rev (e.g. a deletion commit)
        if sha256_bytes(shown.stdout) == want_sha256:
            return shown.stdout
    return None


def merge_three_way(ours: bytes, base: bytes, theirs: bytes) -> tuple[bytes, bool]:
    """git merge-file: apply base→theirs (kit) changes onto ours (plugin).

    Returns (merged_bytes, clean). git merge-file exits with the number
    of conflicts (0..127) or 255 on error.
    """
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        paths = (tdp / "ours", tdp / "base", tdp / "theirs")
        for path, data in zip(paths, (ours, base, theirs)):
            path.write_bytes(data)
        cmd = [
            "git",
            "merge-file",
            "--stdout",
            "-L",
            "plugin (published)",
            "-L",
            "base (rostered kit)",
            "-L",
            "kit (current)",
            *(str(p) for p in paths),
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True)
        except FileNotFoundError as exc:
            raise ResyncError("git is not on PATH — the resync needs it") from exc
    if proc.returncode == 255 or proc.returncode < 0:
        raise ResyncError(
            f"git merge-file failed: {proc.stderr.decode('utf-8', 'replace').strip()}"
        )
    return proc.stdout, proc.returncode == 0


def frontmatter_version(text: str) -> str | None:
    """Extract ``version:`` from a component file's YAML frontmatter."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    for line in text[4:end].splitlines():
        match = re.match(r"^version:\s*[\"']?([^\"'\n]+?)[\"']?\s*$", line)
        if match:
            return match.group(1)
    return None


def _entry_bounds(lines: list[str], name: str) -> tuple[int, int]:
    """Start/end line indices of a component's roster entry.

    Both matches are anchored to the roster's 2-space list indent so a
    ``why: >-`` continuation line that happens to begin with ``- name:``
    (indented deeper) can never open or close an entry (KIT-0110
    evaluator: latent split risk in unanchored matching).
    """
    start = None
    for i, line in enumerate(lines):
        # `==` (rstrip only): exact-entry match at the list indent, so
        # `feature-developer` can never claim `feature-developer-f5`'s
        # block and a deeper-indented lookalike never matches.
        if line.rstrip() == f"  - name: {name}":
            start = i
            break
    if start is None:
        raise ResyncError(f"{name}: no roster entry found for update")
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("  - name:"):
            end = i
            break
    return start, end


# Insertion anchors per field: a missing field is inserted directly after
# the first anchor present, keeping the roster's established field order
# (name, kind, ships, source, kit_version, kit_sha256, plugin_sha256, why).
_FIELD_ANCHORS = {
    "plugin_sha256": ("kit_sha256", "kit_version", "source"),
    "kit_sha256": ("kit_version", "source"),
    "kit_version": ("source",),
}


def set_entry_field(lines: list[str], name: str, field: str, value: str) -> None:
    """Replace or insert one ``field: value`` line in a component's entry.

    Textual, not YAML-roundtrip: the roster's header comments and field
    order are part of its contract and a safe_load/dump cycle would
    destroy them.
    """
    start, end = _entry_bounds(lines, name)
    new_line = f"    {field}: {value}"
    for i in range(start + 1, end):
        if lines[i].lstrip().startswith(f"{field}:"):
            lines[i] = new_line
            return
    for anchor in _FIELD_ANCHORS.get(field, ()):
        for i in range(start + 1, end):
            if lines[i].lstrip().startswith(f"{anchor}:"):
                lines.insert(i + 1, new_line)
                return
    lines.insert(start + 1, new_line)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: never lets a ResyncError escape as a traceback."""
    try:
        return _main(argv)
    except ResyncError as exc:
        print(f"ERROR: {exc}")
        return EXIT_INTEGRITY


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Resync drifted kit components into the published "
        "plugin via three-way merge, and maintain roster.yaml's hash "
        "columns (kit_sha256 + plugin_sha256)."
    )
    parser.add_argument(
        "--kit-root",
        default=str(Path(__file__).resolve().parent.parent.parent),
        help="kit repo root (default: this checkout)",
    )
    parser.add_argument(
        "--marketplace-root",
        required=True,
        help="local checkout of the marketplace repo (movito/agentive-skills)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="emit the work-list only; write nothing",
    )
    parser.add_argument(
        "--hashes-only",
        action="store_true",
        help="skip all body writes; only refresh the plugin_sha256 column",
    )
    args = parser.parse_args(argv)

    kit_root = Path(args.kit_root)
    marketplace_root = Path(args.marketplace_root)
    plugin_dir = marketplace_root / PLUGIN_REL
    roster_path = marketplace_root / ROSTER_REL

    if not (kit_root / ".claude").is_dir():
        print(f"ERROR: {kit_root} has no .claude/ directory — wrong --kit-root?")
        return EXIT_USAGE
    if not (kit_root / ".git").exists():
        print(f"ERROR: {kit_root} is not a git checkout — history walk impossible.")
        return EXIT_USAGE
    if not roster_path.is_file():
        print(f"ERROR: no roster at {roster_path} — wrong --marketplace-root?")
        return EXIT_USAGE

    roster_text = roster_path.read_text(encoding="utf-8")
    components = _guard.parse_roster(roster_text)  # SystemExit 2/4 on bad roster
    validate_shipped(components)

    shipped = [c for c in components if c.get("ships", False)]

    # ---- Work-list: roster-hash delta, never git diff (KIT-0099) ----
    drifted: list[dict] = []
    for comp in shipped:
        source = comp.get("source")
        recorded = comp.get("kit_sha256")
        if source is None or recorded is None:
            print(
                f"ERROR: {comp['name']}: ships=true but roster lacks "
                "source/kit_sha256 — fix the roster first (the drift guard "
                "flags this too)."
            )
            return EXIT_ROSTER_IO
        kit_file = kit_root / source
        if not kit_file.is_file():
            print(
                f"ERROR: {comp['name']}: rostered source {source} is missing "
                "from the kit — resolve the rename/deletion before resyncing."
            )
            return EXIT_INTEGRITY
        if sha256_bytes(kit_file.read_bytes()) != recorded:
            drifted.append(comp)

    if drifted:
        print(f"work-list: {len(drifted)} drifted component(s)")
        for comp in drifted:
            print(f"  - {comp['name']} ({comp['source']})")
    else:
        print("work-list: empty — kit matches the rostered hashes.")

    if args.dry_run:
        return EXIT_OK

    roster_lines = roster_text.splitlines()

    if args.hashes_only:
        if drifted:
            print(
                "note: --hashes-only leaves the above drift untouched; the "
                "column is computed from the published bodies as they are."
            )
        missing = []
        for comp in shipped:
            body = plugin_dir / plugin_body_relpath(comp)
            if not body.is_file():
                missing.append(f"{comp['name']}: no published body at {body}")
                continue
            set_entry_field(
                roster_lines,
                comp["name"],
                "plugin_sha256",
                sha256_bytes(body.read_bytes()),
            )
        if missing:
            print("ERROR: cannot hash missing bodies (run a full resync):")
            for m in missing:
                print(f"  - {m}")
            return EXIT_INTEGRITY
        roster_path.write_text("\n".join(roster_lines) + "\n", encoding="utf-8")
        print(f"plugin_sha256 refreshed for {len(shipped)} shipped component(s).")
        return EXIT_OK

    # ---- Base lookup for every drifted component BEFORE any write ----
    # (base-not-found aborts the whole run with nothing written; a silent
    # partial state would be worse than the drift.)
    bases: dict[str, bytes | None] = {}
    not_found: list[str] = []
    for comp in drifted:
        body = plugin_dir / plugin_body_relpath(comp)
        if not body.is_file():
            bases[comp["name"]] = None  # new component: copy, no merge needed
            continue
        base = find_base_content(kit_root, comp["source"], comp["kit_sha256"])
        if base is None:
            not_found.append(
                f"{comp['name']}: no version of {comp['source']} in kit "
                f"history hashes to rostered {comp['kit_sha256'][:12]}… — "
                "content never committed, or the file was renamed. Refusing "
                "to fall back to a copy; fix the roster or history first."
            )
            continue
        bases[comp["name"]] = base
    if not_found:
        print("ERROR: three-way merge base not found:")
        for line in not_found:
            print(f"  - {line}")
        return EXIT_INTEGRITY

    # ---- Merge and write ----
    conflicts: list[str] = []
    for comp in drifted:
        name = comp["name"]
        body = plugin_dir / plugin_body_relpath(comp)
        theirs = (kit_root / comp["source"]).read_bytes()
        if not body.is_file():
            body.parent.mkdir(parents=True, exist_ok=True)
            body.write_bytes(theirs)
            print(f"  {name}: COPIED (new component, no published body yet)")
        else:
            merged, clean = merge_three_way(body.read_bytes(), bases[name], theirs)
            if not clean:
                conflict_path = body.with_name(body.name + ".conflict")
                conflict_path.write_bytes(merged)
                conflicts.append(name)
                print(
                    f"  {name}: CONFLICT — published body left untouched; "
                    f"resolve {conflict_path} by hand, then re-run"
                )
                continue
            body.write_bytes(merged)
            print(f"  {name}: merged clean")
        new_kit_sha = sha256_bytes(theirs)
        set_entry_field(roster_lines, name, "kit_sha256", new_kit_sha)
        version = frontmatter_version(theirs.decode("utf-8", "replace"))
        if version is not None:
            set_entry_field(roster_lines, name, "kit_version", f'"{version}"')

    # ---- plugin_sha256 for every shipped component (R2's input) ----
    for comp in shipped:
        # Conflicted components keep their current published body, so the
        # recomputed hash is still the truth about what ships.
        body = plugin_dir / plugin_body_relpath(comp)
        if not body.is_file():
            print(f"ERROR: {comp['name']}: published body still missing at {body}")
            return EXIT_INTEGRITY
        set_entry_field(
            roster_lines,
            comp["name"],
            "plugin_sha256",
            sha256_bytes(body.read_bytes()),
        )

    roster_path.write_text("\n".join(roster_lines) + "\n", encoding="utf-8")

    if conflicts:
        print(
            f"\n{len(conflicts)} conflict(s) surfaced ({', '.join(conflicts)}) — "
            "roster hash columns updated for clean merges only."
        )
        return EXIT_CONFLICTS
    resynced = len(drifted)
    print(
        f"\nresync complete: {resynced} component(s) merged, "
        f"plugin_sha256 refreshed for {len(shipped)} shipped."
    )
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
