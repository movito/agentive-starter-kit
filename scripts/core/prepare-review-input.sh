#!/bin/bash
# Prepare an adversarial code-review input file for the given task.
# Usage: ./scripts/core/prepare-review-input.sh <TASK-ID> [--base main] [--format diff|full] [--help]
#
# Metadata:
#   version: 2.0.0
#   origin: agentive-starter-kit
#   last-updated: 2026-08-07
#   created-by: "@movito with feature-developer-f5"
#
# ─── One-release deprecation shim (KIT-0091 F3, KIT-ADR-0028 1b) ───
# The implementation moved to agentive_kit.review_input — same
# arguments, same output file (.adversarial/inputs/<TASK>-code-review-
# input.md), same cross-repo Path routing and exit codes. The parity
# record binding the port to the old bash behavior lives in
# tests/test_prepare_review_input.py (KIT-0091 F2).
#
# Changes directory to its own repo root before delegating (the module discovers the
# project from CWD — the BugBot PR #112 anchoring lesson), and follows
# the scripts/core/project resolution order: installed agentive-kit
# first, then the in-repo package source, then a loud refusal.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PKG_SRC="$SCRIPT_DIR/../../packages/agentive-kit/src"

cd "$PROJECT_ROOT" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is required — prepare-review-input.sh is now a shim over the agentive-kit package" >&2
    exit 1
fi

if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    echo "ERROR: python3 >= 3.10 is required by agentive-kit (found: $(python3 --version 2>&1))" >&2
    exit 1
fi

AGENTIVE_KIT_SRC="$PKG_SRC" exec python3 - "$@" <<'PY'
import os
import sys

try:
    from agentive_kit import review_input
except ImportError:
    pkg_src = os.environ.get("AGENTIVE_KIT_SRC", "")
    if pkg_src and os.path.isdir(os.path.join(pkg_src, "agentive_kit")):
        sys.path.insert(0, pkg_src)
    try:
        from agentive_kit import review_input
    except ImportError as exc:
        print("ERROR: agentive-kit is not installed", file=sys.stderr)
        print(
            "   Review-input assembly lives in the agentive-kit package"
            " (KIT-ADR-0028).",
            file=sys.stderr,
        )
        print("   Install it:", file=sys.stderr)
        print("     uv tool install agentive-kit", file=sys.stderr)
        print("   or: pip install agentive-kit", file=sys.stderr)
        print(f"   (import failed: {exc})", file=sys.stderr)
        sys.exit(1)

review_input.main(sys.argv[1:])
PY
