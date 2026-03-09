#!/usr/bin/env bash
# ---
# name: check-sync.sh
# description: Check if core scripts are in sync with agentive-starter-kit
# version: 1.0.0
# origin: agentive-starter-kit
# ---

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$SCRIPT_DIR/../.core-manifest.json"
VERSION_FILE="$SCRIPT_DIR/VERSION"

if [[ ! -f "$MANIFEST" ]]; then
    echo "❌ No .core-manifest.json found. Run from a project with core scripts installed."
    exit 1
fi

LOCAL_VERSION=$(cat "$VERSION_FILE" 2>/dev/null || echo "unknown")
echo "Core scripts version: $LOCAL_VERSION"
echo "Manifest: $MANIFEST"

# If ASK repo is available locally, compare
if [[ -z "${ASK_REPO:-}" ]]; then
    echo "⚠️  ASK_REPO not set. Set it to your agentive-starter-kit checkout path."
    echo "   Example: ASK_REPO=~/Github/agentive-starter-kit ./scripts/core/check-sync.sh"
    exit 1
fi

ASK_CORE="$ASK_REPO/scripts/core"
if [[ -d "$ASK_CORE" ]]; then
    ASK_VERSION=$(cat "$ASK_CORE/VERSION" 2>/dev/null || echo "unknown")
    echo "Upstream version: $ASK_VERSION"
    echo ""

    DRIFT=0
    # Check local files against upstream
    for f in "$SCRIPT_DIR"/*; do
        fname=$(basename "$f")
        [[ "$fname" == "VERSION" || "$fname" == "check-sync.sh" ]] && continue
        if [[ -f "$ASK_CORE/$fname" ]]; then
            if ! diff -q "$f" "$ASK_CORE/$fname" > /dev/null 2>&1; then
                echo "⚠️  DRIFT: $fname differs from upstream"
                DRIFT=$((DRIFT + 1))
            fi
        fi
    done

    # Check for upstream files missing locally
    for f in "$ASK_CORE"/*; do
        fname=$(basename "$f")
        [[ "$fname" == "VERSION" || "$fname" == "check-sync.sh" ]] && continue
        if [[ ! -f "$SCRIPT_DIR/$fname" ]]; then
            echo "⚠️  MISSING: $fname exists upstream but not locally"
            DRIFT=$((DRIFT + 1))
        fi
    done

    if [[ $DRIFT -eq 0 ]]; then
        echo "✅ All core scripts match upstream ($ASK_VERSION)"
    else
        echo ""
        echo "❌ $DRIFT file(s) have drifted from upstream"
        echo "   Copy the latest files from $ASK_CORE to $SCRIPT_DIR"
        exit 1
    fi
else
    echo "⚠️  ASK repo not found at $ASK_CORE"
    echo "   Verify ASK_REPO points to a valid agentive-starter-kit checkout"
    exit 1
fi
