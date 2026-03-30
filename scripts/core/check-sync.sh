#!/usr/bin/env bash
# ---
# name: check-sync.sh
# description: Check if core scripts are in sync with agentive-starter-kit
# version: 1.0.0
# origin: agentive-starter-kit
# ---

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

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

    # Check .kit/ builder layer (kit repos only)
    ASK_KIT="$ASK_REPO/.kit"
    LOCAL_KIT="$PROJECT_ROOT/.kit"
    if [[ -d "$LOCAL_KIT" && -d "$ASK_KIT" ]]; then
        echo ""
        echo "Checking .kit/ builder layer..."
        KIT_DIRS=("templates" "skills" "launchers" "adr" "docs"
                  "adversarial/scripts" "adversarial/docs" "adversarial/templates"
                  "context/workflows" "context/templates")
        for kdir in "${KIT_DIRS[@]}"; do
            if [[ -d "$ASK_KIT/$kdir" && -d "$LOCAL_KIT/$kdir" ]]; then
                while IFS= read -r f; do
                    rel="${f#"$ASK_KIT/$kdir/"}"
                    local_file="$LOCAL_KIT/$kdir/$rel"
                    if [[ -f "$local_file" ]]; then
                        if ! diff -q "$f" "$local_file" > /dev/null 2>&1; then
                            echo "⚠️  DRIFT: .kit/$kdir/$rel differs from upstream"
                            DRIFT=$((DRIFT + 1))
                        fi
                    else
                        echo "⚠️  MISSING: .kit/$kdir/$rel exists upstream but not locally"
                        DRIFT=$((DRIFT + 1))
                    fi
                done < <(find "$ASK_KIT/$kdir" -type f)
            fi
        done
        # Check individual kit files
        KIT_FILES=("adversarial/config.yml.template" "context/patterns.yml" "context/AGENT-SYSTEM-GUIDE.md")
        for kf in "${KIT_FILES[@]}"; do
            if [[ -f "$ASK_KIT/$kf" && -f "$LOCAL_KIT/$kf" ]]; then
                if ! diff -q "$ASK_KIT/$kf" "$LOCAL_KIT/$kf" > /dev/null 2>&1; then
                    echo "⚠️  DRIFT: .kit/$kf differs from upstream"
                    DRIFT=$((DRIFT + 1))
                fi
            elif [[ -f "$ASK_KIT/$kf" && ! -f "$LOCAL_KIT/$kf" ]]; then
                echo "⚠️  MISSING: .kit/$kf exists upstream but not locally"
                DRIFT=$((DRIFT + 1))
            fi
        done
    fi

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
