#!/usr/bin/env bash
# Create a fully-provisioned per-task worktree for an implementation session.
#
# Usage:
#   ./scripts/local/new-worktree.sh <TASK-ID> [slug]
#
# ─── Thin delegator (KIT-0091 F3, KIT-ADR-0028 1b) ───
# The provisioning LIBRARY now lives in agentive_kit.worktree — the
# KIT-0043/0044 recipe (fresh origin/main, enumerated symlinks, real
# per-worktree venv, per-worktree Serena config) is implemented there
# and pinned by tests/test_new_worktree.py, which drives THIS script
# end-to-end. This entry script stays in scripts/local as the door
# surface (any door change is phase 2).
#
# The module resolves the PRIMARY clone from this script's location
# (via the shared git common dir — never the caller's cwd), so
# invoking a worktree's own copy still targets the shared primary.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_SRC="$SCRIPT_DIR/../../packages/agentive-kit/src"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is required — new-worktree.sh delegates to the agentive-kit package" >&2
    exit 1
fi

if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    echo "ERROR: python3 >= 3.10 is required by agentive-kit (found: $(python3 --version 2>&1))" >&2
    exit 1
fi

NEW_WORKTREE_ANCHOR="$SCRIPT_DIR" AGENTIVE_KIT_SRC="$PKG_SRC" \
    exec python3 - "$@" <<'PY'
import os
import sys
from pathlib import Path

try:
    from agentive_kit import worktree
except ImportError:
    pkg_src = os.environ.get("AGENTIVE_KIT_SRC", "")
    if pkg_src and os.path.isdir(os.path.join(pkg_src, "agentive_kit")):
        sys.path.insert(0, pkg_src)
    try:
        from agentive_kit import worktree
    except ImportError as exc:
        print("Error: agentive-kit is not installed", file=sys.stderr)
        print(
            "   The worktree library lives in the agentive-kit package"
            " (KIT-ADR-0028).",
            file=sys.stderr,
        )
        print("   Install it:", file=sys.stderr)
        print("     uv tool install agentive-kit", file=sys.stderr)
        print("   or: pip install agentive-kit", file=sys.stderr)
        print(f"   (import failed: {exc})", file=sys.stderr)
        sys.exit(1)

worktree.main(sys.argv[1:], anchor=Path(os.environ["NEW_WORKTREE_ANCHOR"]))
PY
