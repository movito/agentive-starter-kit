#!/bin/bash
# Run all 7 preflight gates for a PR
# Usage: ./scripts/core/preflight-check.sh [--pr PR_NUMBER] [--task TASK_ID] [--repo owner/name] [--help]
#
# Metadata:
#   version: 2.0.0
#   origin: agentive-starter-kit
#   last-updated: 2026-08-07
#   created-by: "@movito with feature-developer-f5"
#
# ─── One-release deprecation shim (KIT-0091 F3, KIT-ADR-0028 1b) ───
# The implementation moved to the agentive-kit package
# (agentive_kit.preflight) — same flags, same GATE:<n>:<name>:<verdict>
# output contract, same exit codes (0 pass / 1 fail / 2 pending). The
# parity record binding the port to the old bash behavior lives in
# tests/test_preflight_check.py (KIT-0091 F2).
#
# Prefer the package CLI directly:
#     agentive preflight [--pr N] [--task ID] [--repo owner/name]
#
# This shim follows the scripts/core/project resolution order: an
# installed agentive-kit first (the phase-3 end state), then the kit
# repo's own packages/agentive-kit/src tree (dogfood), then a loud
# refusal — never a silent fallback.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_SRC="$SCRIPT_DIR/../../packages/agentive-kit/src"

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is required — preflight-check.sh is now a shim over the agentive-kit package" >&2
    exit 1
fi

AGENTIVE_KIT_SRC="$PKG_SRC" exec python3 - "$@" <<'PY'
import os
import sys

try:
    from agentive_kit import preflight
except ModuleNotFoundError:
    pkg_src = os.environ.get("AGENTIVE_KIT_SRC", "")
    if pkg_src and os.path.isdir(os.path.join(pkg_src, "agentive_kit")):
        sys.path.insert(0, pkg_src)
    try:
        from agentive_kit import preflight
    except ModuleNotFoundError:
        print("ERROR: agentive-kit is not installed")
        print("   The preflight gates live in the agentive-kit package (KIT-ADR-0028).")
        print("   Install it:")
        print("     uv tool install agentive-kit")
        print("   or: pip install agentive-kit")
        sys.exit(1)

preflight.main(sys.argv[1:])
PY
