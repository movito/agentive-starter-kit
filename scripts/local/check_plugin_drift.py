#!/usr/bin/env python3
"""Plugin drift guard (KIT-0096 F4): fail when kit .claude/ outruns the release.

Compares the kit's canonical ``.claude/`` component files against the roster
published with the last ``agentive-workflow`` plugin release
(``plugins/agentive-workflow/roster.yaml`` in movito/agentive-skills). The
roster records, per shipped component, the sha256 of the KIT source file the
plugin copy was derived from. Two failure classes:

1. **Content drift** — a shipped component's kit file no longer matches the
   hash recorded at release time (the kit is newer than the published
   plugin), or a rostered source file is gone (renamed/deleted without a
   release).
2. **Roster drift** — a component file exists under ``.claude/`` with no
   roster entry at all (a new agent/command/skill was added without a
   deliberate ships/kit-side decision — KIT-0067's function-enumeration law).

This is the automated replacement for the withdrawn checklist option: the
June→August 2026 staleness (plugin shipping v6/v7-era agents, no planner)
recurs silently without it. Kit-internal: lives in ``scripts/local/`` and is
NOT synced to consumer projects (their ``.claude/`` comes from the plugin).

Runs in CI only — it fetches the roster over the network by default, so it
must never be wired into pre-commit. Exit codes follow the kit convention:
``0`` in sync, ``1`` drift detected, ``2`` usage/environment error,
``4`` roster fetch/parse error.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_ROSTER_URL = (
    "https://raw.githubusercontent.com/movito/agentive-skills/main/"
    "plugins/agentive-workflow/roster.yaml"
)

# Component files that must each have a roster entry (globs relative to
# the kit root). Mirrors the plugin's component kinds.
COMPONENT_GLOBS = (
    ".claude/agents/*.md",
    ".claude/commands/*.md",
    ".claude/skills/*/SKILL.md",
)

EXIT_IN_SYNC = 0
EXIT_DRIFT = 1
EXIT_USAGE = 2
EXIT_ROSTER_IO = 4


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_roster_text(roster_file: str | None, roster_url: str) -> str:
    """Return roster YAML text from a local file or over HTTP."""
    if roster_file is not None:
        path = Path(roster_file)
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"ERROR: cannot read roster file {path}: {exc}")
            raise SystemExit(EXIT_ROSTER_IO) from exc
    try:
        with urllib.request.urlopen(roster_url, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, OSError, ValueError) as exc:
        print(f"ERROR: cannot fetch roster from {roster_url}: {exc}")
        raise SystemExit(EXIT_ROSTER_IO) from exc


def parse_roster(text: str) -> list[dict]:
    """Parse roster YAML and return the components list."""
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - environment guard
        print("ERROR: PyYAML is required (pip install pyyaml).")
        raise SystemExit(EXIT_USAGE) from exc
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        print(f"ERROR: roster is not valid YAML: {exc}")
        raise SystemExit(EXIT_ROSTER_IO) from exc
    if not isinstance(data, dict) or not isinstance(data.get("components"), list):
        print("ERROR: roster has no 'components' list.")
        raise SystemExit(EXIT_ROSTER_IO)
    return data["components"]


def _contained_source(kit_root: Path, source: str) -> Path | None:
    """Resolve a roster source path, refusing escapes outside kit_root.

    The roster is fetched over the network; a source like ``../secrets`` or
    an absolute path must never be hashed. Returns None when the path
    escapes the kit root.
    """
    if Path(source).is_absolute():
        return None
    resolved = (kit_root / source).resolve()
    try:
        resolved.relative_to(kit_root.resolve())
    except ValueError:
        return None
    return resolved


def check_drift(kit_root: Path, components: list[dict]) -> list[str]:
    """Return a list of drift findings (empty = in sync)."""
    findings: list[str] = []
    rostered_sources: set[str] = set()

    for comp in components:
        name = comp.get("name", "<unnamed>")
        source = comp.get("source")
        if source is not None:
            if source in rostered_sources:
                findings.append(
                    f"{name}: duplicate roster entry for source {source} — "
                    "roster is malformed; fix it and re-release"
                )
                continue
            rostered_sources.add(source)
        if not comp.get("ships", False):
            continue
        if source is None:
            findings.append(f"{name}: ships=true but no source path in roster")
            continue
        path = _contained_source(kit_root, source)
        if path is None:
            findings.append(
                f"{name}: rostered source {source} escapes the kit root — "
                "refusing to hash it; fix the roster"
            )
            continue
        if not path.is_file():
            findings.append(
                f"{name}: rostered source {source} is missing from the kit "
                "(renamed or deleted without a plugin release)"
            )
            continue
        recorded = comp.get("kit_sha256")
        if recorded is None:
            findings.append(f"{name}: ships=true but no kit_sha256 in roster")
            continue
        try:
            actual = sha256_of(path)
        except OSError as exc:
            findings.append(f"{name}: cannot read {source} for hashing: {exc}")
            continue
        if actual != recorded:
            findings.append(
                f"{name}: kit content is newer than the published release "
                f"({source}: {actual[:12]}… != rostered {recorded[:12]}…)"
            )

    for pattern in COMPONENT_GLOBS:
        for path in sorted(kit_root.glob(pattern)):
            rel = path.relative_to(kit_root).as_posix()
            if rel not in rostered_sources:
                findings.append(
                    f"unrostered component: {rel} has no roster entry — "
                    "decide ships/kit-side and cut a release (or record it "
                    "kit-side in roster.yaml)"
                )

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail when kit .claude/ content is newer than the last "
        "published agentive-workflow plugin release."
    )
    parser.add_argument(
        "--roster-file",
        help="local roster.yaml path (skips the network fetch; used by tests)",
    )
    parser.add_argument(
        "--roster-url",
        default=DEFAULT_ROSTER_URL,
        help=f"roster URL (default: {DEFAULT_ROSTER_URL})",
    )
    parser.add_argument(
        "--kit-root",
        default=str(Path(__file__).resolve().parent.parent.parent),
        help="kit repo root (default: this checkout)",
    )
    args = parser.parse_args(argv)

    kit_root = Path(args.kit_root)
    if not (kit_root / ".claude").is_dir():
        print(f"ERROR: {kit_root} has no .claude/ directory — wrong --kit-root?")
        return EXIT_USAGE

    text = load_roster_text(args.roster_file, args.roster_url)
    components = parse_roster(text)
    findings = check_drift(kit_root, components)

    if findings:
        print(
            f"PLUGIN DRIFT: {len(findings)} finding(s) — the published "
            "agentive-workflow release is stale relative to this kit tree."
        )
        for f in findings:
            print(f"  - {f}")
        print(
            "\nRemedy: cut a plugin release (refresh content into "
            "movito/agentive-skills, update roster.yaml hashes, bump the "
            "plugin version) — see plugins/agentive-workflow/roster.yaml "
            "header and KIT-0096."
        )
        return EXIT_DRIFT

    shipped = sum(1 for c in components if c.get("ships", False))
    print(f"in sync: {shipped} shipped components match the published roster.")
    return EXIT_IN_SYNC


if __name__ == "__main__":
    sys.exit(main())
