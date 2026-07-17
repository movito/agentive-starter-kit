#!/usr/bin/env bash
# DEPRECATED shim (KIT-0053): use scripts/local/bootstrap --new instead.
# Removal is filed and pinned to the next minor release (KIT-0054).
#
# Preserves the historical create-project.sh flag surface (help text,
# error forms, exit codes — pinned by tests/test_entrance_shims.py),
# then execs the setup door, which orchestrates the export engine.
#
# Kit-side entrance: the door lives in scripts/local/, which is never
# synced to consumers. In a consumer checkout this shim fails loudly
# with guidance instead of exporting a half-configured tree.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOOR="$SCRIPT_DIR/../local/bootstrap"

# --- Parse arguments (historical surface) ---
TARGET_DIR=""
PROJECT_NAME=""
TASK_PREFIX=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --name)    PROJECT_NAME="$2"; shift 2 ;;
        --prefix)  TASK_PREFIX="$2"; shift 2 ;;
        --help|-h)
            echo "Usage: $0 <target-dir> [--name NAME] [--prefix PREFIX]"
            echo ""
            echo "  <target-dir>     Where to create the new project (must not exist)"
            echo "  --name NAME      Project name (default: directory basename)"
            echo "  --prefix PREFIX  Task ID prefix, e.g. ID2 (default: derived from name)"
            echo ""
            echo "Example:"
            echo "  $0 ~/Github/my-new-project --name 'My New Project' --prefix MNP"
            exit 0
            ;;
        *)
            if [[ -z "$TARGET_DIR" ]]; then
                TARGET_DIR="$1"
            else
                echo "Error: unexpected argument '$1'" >&2
                exit 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$TARGET_DIR" ]]; then
    echo "Error: target directory is required" >&2
    echo "Usage: $0 <target-dir> [--name NAME] [--prefix PREFIX]" >&2
    exit 1
fi

# Expand ~ and resolve path
TARGET_DIR="${TARGET_DIR/#\~/$HOME}"

if [[ -e "$TARGET_DIR" ]]; then
    echo "Error: '$TARGET_DIR' already exists" >&2
    exit 1
fi

if [[ ! -x "$DOOR" ]]; then
    echo "Error: the kit setup door is not present ($DOOR)." >&2
    echo "  create-project.sh is a kit-side entrance — run it from an" >&2
    echo "  agentive-starter-kit clone: scripts/local/bootstrap --new <dir>" >&2
    exit 1
fi

set -- --new "$TARGET_DIR" --legacy-shim
[[ -n "$PROJECT_NAME" ]] && set -- "$@" --name "$PROJECT_NAME"
[[ -n "$TASK_PREFIX" ]] && set -- "$@" --prefix "$TASK_PREFIX"
exec "$DOOR" "$@"
