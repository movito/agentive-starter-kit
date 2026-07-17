#!/usr/bin/env bash
# DEPRECATED shim (KIT-0053): use
#   scripts/local/bootstrap --adopt <dir> --design-materials
# instead. Removal is filed and pinned to the next minor release
# (KIT-0054).
#
# Preserves the historical bootstrap.sh surface (one positional target,
# pinned by tests/test_entrance_shims.py), then execs the setup door,
# which hands off to the design-materials engine.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOOR="$SCRIPT_DIR/bootstrap"

TARGET="${1:?Usage: $0 <target-directory>}"
if [ ! -d "$TARGET" ]; then
    echo "❌ Target directory does not exist: $TARGET"
    echo "   Create it first and put your design materials in it."
    exit 1
fi

exec "$DOOR" --adopt "$TARGET" --design-materials --legacy-shim
