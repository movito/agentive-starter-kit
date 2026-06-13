#!/bin/bash
# scripts/core/lib/target_repo.sh — cross-repo awareness helper
#
# Metadata:
#   version: 1.0.0
#   origin: ixda-services-2.0 (ID2-0014)
#   last-updated: 2026-04-20
#   created-by: "@movito with feature-developer-v6"
#
# Source this file from scripts that need to operate against a GitHub
# repository other than the one rooted at the current working directory
# (the "planning repo"). Used by the cross-repo workflow where planning
# and code live in sibling repos.
#
# CLAUDE.md "## Target Repository" format contract:
#
#     ## Target Repository
#
#     ...
#     - **Path**: `../ixda-services`
#     - **GitHub**: `movito/ixda-services`
#
# Both `Path` and `GitHub` must be bullet list items under the
# `## Target Repository` heading, with values in backticks. The section
# is optional — single-repo projects set no such section and the helper
# becomes a no-op.
#
# Usage
# -----
#
#   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#   # shellcheck disable=SC1091
#   . "$SCRIPT_DIR/lib/target_repo.sh"
#
#   # Parse caller's args first, then:
#   target_repo_init [--repo owner/name]
#
# After `target_repo_init` returns, these variables are populated:
#
#   TARGET_REPO   — "owner/name" (empty in single-repo mode)
#   TARGET_PATH   — "../sibling" filesystem path (empty in single-repo mode)
#   GH_REPO_ARG   — "--repo owner/name" (empty in single-repo mode)
#   GIT_DIR_ARG   — "-C ../sibling"    (empty in single-repo mode)
#
# Use `GH_REPO_ARG` and `GIT_DIR_ARG` unquoted so that they expand to
# either the flag pair or nothing:
#
#   gh $GH_REPO_ARG pr view --json number
#   git $GIT_DIR_ARG branch --show-current
#
# This relies on word splitting and therefore assumes `TARGET_REPO` and
# `TARGET_PATH` contain no whitespace. GitHub `owner/name` slugs cannot
# contain whitespace, and sibling-repo paths in this workflow are simple
# (e.g. `../ixda-services`), so the assumption is safe in practice.
#
# An explicit `--repo owner/name` argument to `target_repo_init` always
# wins over anything parsed from CLAUDE.md — the caller is expected to
# extract its own `--repo` flag first and forward it here.
#
# Helpers:
#   target_repo_is_set — returns 0 if TARGET_REPO is non-empty

if [ -n "${_TARGET_REPO_LIB_LOADED:-}" ]; then
    return 0 2>/dev/null || true
fi
_TARGET_REPO_LIB_LOADED=1

TARGET_REPO="${TARGET_REPO:-}"
TARGET_PATH="${TARGET_PATH:-}"
GH_REPO_ARG=""
GIT_DIR_ARG=""

# Locate CLAUDE.md. Resolution order:
#   1. explicit $PROJECT_ROOT (caller-supplied)
#   2. three-levels-up from this library (scripts/core/lib -> project root)
#   3. git rev-parse --show-toplevel (survives if the library is relocated)
_target_repo_find_claude_md() {
    if [ -n "${PROJECT_ROOT:-}" ] && [ -f "$PROJECT_ROOT/CLAUDE.md" ]; then
        printf '%s\n' "$PROJECT_ROOT/CLAUDE.md"
        return 0
    fi
    local lib_dir root
    lib_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || lib_dir=""
    if [ -n "$lib_dir" ]; then
        root="$(cd "$lib_dir/../../.." 2>/dev/null && pwd)" || root=""
        if [ -n "$root" ] && [ -f "$root/CLAUDE.md" ]; then
            printf '%s\n' "$root/CLAUDE.md"
            return 0
        fi
    fi
    # Fallback: ask git for the repo root. Works even if this lib is
    # sourced from an unexpected path.
    if command -v git >/dev/null 2>&1; then
        root=$(git rev-parse --show-toplevel 2>/dev/null) || root=""
        if [ -n "$root" ] && [ -f "$root/CLAUDE.md" ]; then
            printf '%s\n' "$root/CLAUDE.md"
            return 0
        fi
    fi
    return 1
}

# Extract "owner/name" and "path" from the "## Target Repository" section
# of CLAUDE.md. Only fills in TARGET_REPO / TARGET_PATH when currently empty.
_target_repo_parse_claude_md() {
    local claude_md section
    claude_md=$(_target_repo_find_claude_md) || return 0

    # Isolate the target-repository section (between its heading and the
    # next top-level `## ` heading). awk is portable across bash versions.
    section=$(awk '
        /^## Target Repository[[:space:]]*$/ { in_section = 1; next }
        in_section && /^## / { exit }
        in_section { print }
    ' "$claude_md" 2>/dev/null)
    [ -z "$section" ] && return 0

    if [ -z "$TARGET_REPO" ]; then
        TARGET_REPO=$(printf '%s\n' "$section" \
            | sed -n 's/^- \*\*GitHub\*\*:.*`\([^`]*\)`.*/\1/p' \
            | head -1)
    fi
    if [ -z "$TARGET_PATH" ]; then
        TARGET_PATH=$(printf '%s\n' "$section" \
            | sed -n 's/^- \*\*Path\*\*:.*`\([^`]*\)`.*/\1/p' \
            | head -1)
    fi
}

# Validate that TARGET_REPO (if set) looks like "owner/name".
_target_repo_validate() {
    if [ -z "$TARGET_REPO" ]; then
        return 0
    fi
    if ! printf '%s' "$TARGET_REPO" | grep -qE '^[^/[:space:]]+/[^/[:space:]]+$'; then
        echo "ERROR: target repo must be in owner/name format, got: '$TARGET_REPO'" >&2
        return 1
    fi
}

# Public: initialize TARGET_REPO / TARGET_PATH / GH_REPO_ARG / GIT_DIR_ARG.
# Optional argument pair: --repo owner/name (wins over CLAUDE.md).
target_repo_init() {
    local override=""
    while [ $# -gt 0 ]; do
        case "$1" in
            --repo)
                # Defense-in-depth: catch callers that forget to validate
                # their own --repo argument before forwarding it here.
                if [ -z "${2:-}" ] || [ "${2#-}" != "${2}" ]; then
                    echo "ERROR: --repo requires an owner/name value" >&2
                    return 1
                fi
                override="$2"
                shift 2
                ;;
            --repo=*)
                override="${1#--repo=}"
                if [ -z "$override" ]; then
                    echo "ERROR: --repo= requires an owner/name value" >&2
                    return 1
                fi
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    # Reset so repeated calls are idempotent.
    TARGET_REPO=""
    TARGET_PATH=""

    if [ -n "$override" ]; then
        TARGET_REPO="$override"
        # Intentionally leave TARGET_PATH empty when overriding via --repo:
        # the caller knows the repo but not necessarily the local path.
    else
        _target_repo_parse_claude_md
    fi

    _target_repo_validate || return 1

    if [ -n "$TARGET_REPO" ]; then
        GH_REPO_ARG="--repo $TARGET_REPO"
    else
        GH_REPO_ARG=""
    fi
    if [ -n "$TARGET_PATH" ]; then
        GIT_DIR_ARG="-C $TARGET_PATH"
        # Non-fatal sanity check: warn if TARGET_PATH doesn't look like a
        # git working tree. Caller can still proceed (e.g., if the sibling
        # will be cloned later), but cryptic `fatal: not a git repository`
        # errors from downstream `git -C` calls are now easier to diagnose.
        if [ ! -d "$TARGET_PATH/.git" ] && [ ! -f "$TARGET_PATH/.git" ]; then
            echo "WARNING: TARGET_PATH '$TARGET_PATH' is not a git working tree — git operations via \$GIT_DIR_ARG will fail" >&2
        fi
    else
        GIT_DIR_ARG=""
    fi
}

target_repo_is_set() {
    [ -n "${TARGET_REPO:-}" ]
}
