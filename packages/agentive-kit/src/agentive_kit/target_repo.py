"""Cross-repo target resolution (KIT-0091 — port of lib/target_repo.sh).

The bash originals shared one sourced library for the ID2-0014
cross-repo pattern; the package keeps that single home. ``resolve()``
reads the optional ``## Target Repository`` section of the project's
CLAUDE.md (``- **Path**``/``- **GitHub**`` bullets, values in
backticks) unless an explicit ``--repo`` override wins.

Behavior pinned by the preflight and review-input parity matrices:

- CRLF-checked-out CLAUDE.md parses (the bash awk header pattern's
  ``[[:space:]]*`` swallowed a CR — o3, PR 1 round 2).
- Bullet values are matched per-LINE, mirroring the sed originals
  (greedy last-backtick-span on the line, first matching line wins);
  a multiline regex would let ``[^`]*`` cross newlines and capture
  garbage between bullets (caught by test_preflight_pkg.py).
- Layer 1 of two: this module applies the lib's looser shape check
  (``^[^/\\s]+/[^/\\s]+$``); callers that interpolate the slug into a
  GraphQL query MUST additionally run the strict charset check
  (preflight's ``^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$``) before use
  (KIT-0043).
- A configured path that is not a git working tree WARNs on stderr but
  does not fail here — callers decide fatality (review-input refuses,
  preflight proceeds to a failing git call).
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TargetRepo:
    """Cross-repo routing resolved from --repo or CLAUDE.md (ID2-0014)."""

    repo: str = ""  # owner/name; empty in single-repo mode
    path: str = ""  # local working-tree path; empty unless CLAUDE.md set it

    @property
    def is_set(self) -> bool:
        return bool(self.repo)


def resolve(root: Path, override: str = "") -> TargetRepo:
    """Port of ``target_repo_init``: override wins over CLAUDE.md; the
    section is optional (single-repo projects resolve to an empty
    TargetRepo). Exits 1 with the lib's message on a malformed slug."""
    target = TargetRepo()
    if override:
        target.repo = override
        # Path stays empty on override: the caller knows the repo but
        # not necessarily the local working tree.
    else:
        claude_md = root / "CLAUDE.md"
        if claude_md.is_file():
            try:
                text = claude_md.read_text(encoding="utf-8")
            except OSError:
                text = ""
            section_match = re.search(
                r"^## Target Repository[ \t]*\r?$(.*?)(?=^## |\Z)",
                text,
                re.MULTILINE | re.DOTALL,
            )
            if section_match:
                for line in section_match.group(1).splitlines():
                    if not target.repo:
                        gh_match = re.match(r"- \*\*GitHub\*\*:.*`([^`]*)`", line)
                        if gh_match:
                            target.repo = gh_match.group(1)
                    if not target.path:
                        path_match = re.match(r"- \*\*Path\*\*:.*`([^`]*)`", line)
                        if path_match:
                            target.path = path_match.group(1)

    if target.repo and not re.match(r"^[^/\s]+/[^/\s]+$", target.repo):
        print(
            f"ERROR: target repo must be in owner/name format, got: '{target.repo}'",
            file=sys.stderr,
        )
        sys.exit(1)

    if target.path:
        tree = Path(root, target.path)
        if not (tree / ".git").is_dir() and not (tree / ".git").is_file():
            print(
                f"WARNING: TARGET_PATH '{target.path}' is not a git working tree "
                "— git operations via $GIT_DIR_ARG will fail",
                file=sys.stderr,
            )
    return target
