#!/usr/bin/env bash
# DEPRECATED shim (KIT-0053): use scripts/local/bootstrap --adopt instead.
# Removal is filed and pinned to the next minor release (KIT-0054).
#
# Preserves the historical bootstrap-consumer.sh flag surface
# byte-for-byte (parse + validation messages + exit codes, pinned by
# tests/test_bootstrap_shapes.py), then execs the setup door, which
# orchestrates the consumer engine. This frozen copy of the historical
# validation is a compatibility façade, not a second matrix owner — it
# dies with the shim.

set -e
IFS=$' \t\n'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DOOR="$SCRIPT_DIR/bootstrap"

KIT_ENABLED=1
TARGET=""
SHAPE="single"
PROFILE=""
TARGET_PATH=""
TARGET_GITHUB=""
USAGE="Usage: $0 [--no-kit] [--shape single|planning] [--profile python|none] [--target-path <p>] [--target-github <o/r>] <target-directory>"
while [ $# -gt 0 ]; do
    case "$1" in
        --no-kit)
            KIT_ENABLED=0
            ;;
        --shape)
            shift
            SHAPE="${1:-}"
            ;;
        --shape=*)
            SHAPE="${1#--shape=}"
            ;;
        --profile)
            shift
            PROFILE="${1:-}"
            ;;
        --profile=*)
            PROFILE="${1#--profile=}"
            ;;
        --target-path)
            shift
            TARGET_PATH="${1:-}"
            ;;
        --target-path=*)
            TARGET_PATH="${1#--target-path=}"
            ;;
        --target-github)
            shift
            TARGET_GITHUB="${1:-}"
            ;;
        --target-github=*)
            TARGET_GITHUB="${1#--target-github=}"
            ;;
        --*)
            echo "Error: unknown flag: $1"
            echo "$USAGE"
            exit 1
            ;;
        *)
            if [ -n "$TARGET" ]; then
                echo "Error: multiple target directories given ('$TARGET' and '$1')"
                echo "$USAGE"
                exit 1
            fi
            TARGET="$1"
            ;;
    esac
    if [ $# -gt 0 ]; then shift; fi
done

case "$SHAPE" in
    single|planning) ;;
    *)
        echo "Error: unknown shape: '$SHAPE' (expected: single | planning)"
        echo "$USAGE"
        exit 1
        ;;
esac
if [ "$SHAPE" = "planning" ] && [ "$KIT_ENABLED" -eq 0 ]; then
    echo "Error: --no-kit contradicts --shape planning (the planning shape IS the kit workflow)"
    exit 1
fi
case "$PROFILE" in
    python|none|"") ;;
    *)
        echo "Error: unknown profile: '$PROFILE' (expected: python | none)"
        echo "$USAGE"
        exit 1
        ;;
esac
if [ "$SHAPE" = "planning" ] && [ "$PROFILE" = "python" ]; then
    echo "Error: --profile python contradicts --shape planning (planning forces profile none)"
    exit 1
fi
if [ -n "$TARGET_GITHUB" ] && ! printf '%s' "$TARGET_GITHUB" | grep -qE '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$'; then
    echo "Error: --target-github must look like owner/repo (got: $TARGET_GITHUB)"
    exit 1
fi

if [ -z "$TARGET" ]; then
    echo "$USAGE"
    exit 1
fi
if [ ! -d "$TARGET" ]; then
    echo "Error: Target directory does not exist: $TARGET"
    echo "   Create it first and put your project files in it."
    exit 1
fi
TARGET="$(cd "$TARGET" && pwd)"
if [ "$TARGET" = "$PROJECT_ROOT" ]; then
    echo "Error: target is the kit source repo ($PROJECT_ROOT)."
    echo "   bootstrap-consumer.sh provisions a *consumer* checkout; running it"
    echo "   against the kit itself would rsync/sweep its own files. Aborting."
    exit 1
fi

# Map the validated historical flags onto the door's surface.
set -- --adopt "$TARGET" --shape "$SHAPE" --legacy-shim
[ -n "$PROFILE" ] && set -- "$@" --profile "$PROFILE"
[ "$KIT_ENABLED" -eq 0 ] && set -- "$@" --no-kit
[ -n "$TARGET_PATH" ] && set -- "$@" --target-path "$TARGET_PATH"
[ -n "$TARGET_GITHUB" ] && set -- "$@" --target-github "$TARGET_GITHUB"
exec "$DOOR" "$@"
