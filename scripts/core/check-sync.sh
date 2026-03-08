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
ASK_CORE="${ASK_REPO:-/Users/broadcaster_three/Github/agentive-starter-kit}/scripts/core"
if [[ -d "$ASK_CORE" ]]; then
    ASK_VERSION=$(cat "$ASK_CORE/VERSION" 2>/dev/null || echo "unknown")
    echo "Upstream version: $ASK_VERSION"
    echo ""

    DRIFT=0
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

    if [[ $DRIFT -eq 0 ]]; then
        echo "✅ All core scripts match upstream ($ASK_VERSION)"
    else
        echo ""
        echo "❌ $DRIFT file(s) have drifted from upstream"
        echo "   Run with --apply to pull latest from ASK"
    fi
else
    echo "⚠️  ASK repo not found at $ASK_CORE"
    echo "   Set ASK_REPO env var to point to agentive-starter-kit checkout"
fi
