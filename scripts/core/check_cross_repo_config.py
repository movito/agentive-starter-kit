#!/usr/bin/env python3
"""
Check Cross-Repo Configuration
==============================

Validate that a planning repo which *declares* the cross-repo split also
carries the machine-readable ``## Target Repository`` section in CLAUDE.md
that every cross-repo slash command depends on for auto-detection.

Motivation (KIT-ADR-0024 §2): prose conventions decay. label-maker-planning
declared the split in README prose but silently dropped the parseable
CLAUDE.md section a month after the convention was invented, breaking
auto-routing. Validated conventions survive; this check enforces one.

Semantics:

* FAIL (exit 1) — the repo declares the cross-repo pattern (a concrete
  ``../<name>-code`` sibling path or planning-split prose in README.md or
  CLAUDE.md) but CLAUDE.md has no parseable ``## Target Repository`` section,
  or the section is present but missing its Path/GitHub fields.
* WARN (exit 0) — CLAUDE.md has a parseable section but the target Path does
  not exist on disk. A planning repo must stay usable without the target
  checked out (KIT-0027 §5), so this is a warning, not a failure.
* PASS (exit 0) — either no declaration and no section, or a parseable
  section whose path exists.

Deliberately **not** scanned: ``.claude/agents/`` and ``.claude/commands/``.
Portable cross-repo tooling references the pattern abstractly (and ships
placeholder examples like ``../my-project-code``); those are *support for*
the pattern, not a *declaration* that this specific repo is one half of a
pair. Scanning them would false-positive on the single-repo kit itself.

Usage:
    python scripts/core/check_cross_repo_config.py [repo_root]

Exit codes:
    0 - PASS or WARN
    1 - FAIL
"""

import re
import sys
from pathlib import Path
from typing import NamedTuple, Optional

# A concrete sibling-code path like ``../label-maker-code`` or ``../foo-web``.
# Captures the project stem so placeholder examples can be filtered out.
SIBLING_RE = re.compile(r"\.\./([A-Za-z0-9_.-]+)-(?:code|web)\b")

# Stems that indicate a documentation placeholder, not a real declaration.
PLACEHOLDER_STEMS = frozenset(
    {
        "my-project",
        "your-project",
        "project",
        "project-name",
        "example",
        "example-project",
        "acme",
        "sample",
    }
)

# Prose in README/CLAUDE that unambiguously self-describes a planning repo.
PROSE_RE = re.compile(
    r"planning side of a cross-repo split"
    r"|this is the planning repo"
    r"|the planning side of",
    re.IGNORECASE,
)

# Status sentinels.
PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"

# Sentinel for "heading present but Path/GitHub missing".
MALFORMED = "MALFORMED"


class Result(NamedTuple):
    status: str
    message: str


def _read(path: Path) -> str:
    """Read a text file, returning '' if it does not exist."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except (OSError, UnicodeDecodeError):
        return ""


def declares_cross_repo(text: str) -> bool:
    """True if the text declares THIS repo as one half of a cross-repo pair."""
    if PROSE_RE.search(text):
        return True
    for stem in SIBLING_RE.findall(text):
        if stem not in PLACEHOLDER_STEMS:
            return True
    return False


def parse_target_section(claude_md: str):
    """
    Parse the ``## Target Repository`` section of CLAUDE.md.

    Returns:
        None                          - heading absent
        MALFORMED                     - heading present, Path or GitHub missing
        {"path": ..., "github": ...}  - parseable section
    """
    lines = claude_md.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^##\s+Target Repository\s*$", line):
            start = i
            break
    if start is None:
        return None

    # Collect the section body up to the next level-2 heading.
    body = []
    for line in lines[start + 1 :]:
        if re.match(r"^##\s+\S", line):
            break
        body.append(line)
    section_text = "\n".join(body)

    # Match the runtime contract in scripts/core/lib/target_repo.sh: values
    # MUST be backticked, and GitHub MUST be an `owner/name` slug. Accepting
    # looser input here would let CI PASS configs that runtime cross-repo
    # detection then rejects.
    path_match = re.search(
        r"^\s*[-*]\s*\*\*Path\*\*:\s*`([^`\n]+)`\s*$",
        section_text,
        re.MULTILINE,
    )
    github_match = re.search(
        r"^\s*[-*]\s*\*\*GitHub\*\*:\s*`([^`\n]+)`\s*$",
        section_text,
        re.MULTILINE,
    )
    if path_match is None or github_match is None:
        return MALFORMED

    github = github_match.group(1).strip()
    if re.match(r"^[^/\s]+/[^/\s]+$", github) is None:
        return MALFORMED

    return {
        "path": path_match.group(1).strip(),
        "github": github,
    }


def check(repo_root: Path) -> Result:
    """Run the cross-repo config check against a repo root."""
    readme = _read(repo_root / "README.md")
    claude = _read(repo_root / "CLAUDE.md")

    declared = declares_cross_repo(readme) or declares_cross_repo(claude)
    section = parse_target_section(claude)

    if section is None or section == MALFORMED:
        if declared:
            detail = (
                "section is missing"
                if section is None
                else "section is present but missing Path or GitHub"
            )
            return Result(
                FAIL,
                "Repo declares the cross-repo pattern (concrete ../<name>-code "
                "sibling path or planning-split prose in README/CLAUDE) but the "
                f"machine-readable '## Target Repository' {detail} in CLAUDE.md. "
                "Cross-repo slash commands depend on this section for "
                "auto-routing. Add:\n\n"
                "## Target Repository\n\n"
                "- **Path**: `../<project>-code`\n"
                "- **GitHub**: <owner>/<project>-code",
            )
        return Result(PASS, "Single-repo: no cross-repo declaration, no section.")

    # Parseable section present.
    target_path = (repo_root / section["path"]).resolve()
    if not target_path.exists():
        return Result(
            WARN,
            f"CLAUDE.md '## Target Repository' points to '{section['path']}' "
            f"({section['github']}) which is not checked out locally. The "
            "planning repo stays usable without it; check it out as a sibling "
            "directory when you need to land code.",
        )

    return Result(
        PASS,
        f"Cross-repo config OK: target '{section['path']}' "
        f"({section['github']}) present.",
    )


def main():
    repo_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    result = check(repo_root)

    if result.status == FAIL:
        print(f"❌ Cross-repo config check FAILED:\n\n{result.message}")
        sys.exit(1)
    if result.status == WARN:
        print(f"⚠️  Cross-repo config warning:\n\n{result.message}")
        sys.exit(0)
    print(f"✅ {result.message}")
    sys.exit(0)


if __name__ == "__main__":
    main()
