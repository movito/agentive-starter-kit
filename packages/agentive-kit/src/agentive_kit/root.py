"""Project-root discovery for a globally installed CLI (KIT-0090 F2).

The legacy ``scripts/core/project`` resolved the project from its own
file location (``Path(__file__).resolve().parent.parent.parent``) —
correct for a repo-resident script, meaningless for a tool installed
with ``uv tool install``. The package resolves from the CURRENT
DIRECTORY instead: walk upward until a directory looks like a kit
project root, and refuse loudly when none does. Never operate on a
guessed root.

What counts as a kit project root: a directory containing BOTH a
``.kit/`` directory and a ``CLAUDE.md`` file. Every bootstrapped
consumer (single or planning shape) has both, and so does the
agentive-starter-kit repo itself — which must dogfood this package
(KIT-0090 F5) but, being the upstream rather than a bootstrapped
consumer, carries no ``kit-install`` marker region in its CLAUDE.md.
That is why the marker alone is NOT the discovery test; the marker
stays what it always was — the shape/profile record that doctor reads
once a root is found.
"""

from __future__ import annotations

import os
from pathlib import Path


class RootNotFoundError(Exception):
    """Raised when no kit project root exists at or above the start dir.

    ``str(exc)`` is the full user-facing refusal message, ready to
    print — callers should not need to compose their own.
    """

    def __init__(self, start: Path):
        self.start = start
        super().__init__(
            f"❌ Not inside an agentive project: {start}\n"
            "   Searched this directory and every parent for a project\n"
            "   root (a directory containing both .kit/ and CLAUDE.md)\n"
            "   and found none. Run this command from inside a kit-made\n"
            "   repository, or create one first."
        )


def find_project_root(start: Path | None = None) -> Path:
    """Walk up from ``start`` (default: CWD) to the nearest project root.

    Returns the first ancestor (including ``start`` itself) that
    contains both a ``.kit/`` directory and a ``CLAUDE.md`` file.
    Raises :class:`RootNotFoundError` at the filesystem root.

    The start path is resolved first so the walk terminates even when
    invoked through a relative path or a symlinked working directory;
    a worktree checkout needs nothing special — it carries the full
    tree, so the walk finds its own root, never the primary clone's.
    """
    if start is None:
        # Path.cwd() raises FileNotFoundError if the CWD was deleted
        # from under the process — let that propagate; there is no
        # sensible root to discover from a nonexistent directory.
        start = Path.cwd()
    current = Path(os.path.abspath(start))
    for candidate in (current, *current.parents):
        if (candidate / ".kit").is_dir() and (candidate / "CLAUDE.md").is_file():
            return candidate
    raise RootNotFoundError(current)
