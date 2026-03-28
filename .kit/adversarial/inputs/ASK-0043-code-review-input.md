# Code Review: Agentive Starter Kit — ASK-0043 Root-Resolution Preamble

## Context

Add a standardized root-resolution preamble to all 11 shell scripts so they work
correctly when invoked from any subdirectory, not just the project root. Also fixes
incorrect depth (`..` → `../..`) in 3 scripts after the v0.4.0 restructure.

**Task**: ASK-0043
**PR**: #40
**Bot review status**: BugBot: 2 findings fixed (bootstrap relative path, verify-ci exec path). CodeRabbit: approved after round 2 (4 `|| exit 1` guards added, 1 cosmetic declined).

## Changed Files

### Source: `scripts/core/verify-ci.sh`

```bash
#!/bin/bash
# Check GitHub Actions CI status for a branch
# Usage: ./scripts/verify-ci.sh [branch-name] [--wait]
#
# Options:
#   --wait    Wait for in-progress workflows to complete (default: just report status)
#   --timeout Timeout in seconds for --wait mode (default: 300)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SELF="$SCRIPT_DIR/$(basename "${BASH_SOURCE[0]}")"
cd "$PROJECT_ROOT"

# ... (rest of script unchanged, exec "$SELF" "$BRANCH" at line 200)
```

Key change: Added `SELF` absolute path for `exec` re-invocation. Previously used `exec "$0"` which breaks with relative paths after `cd "$PROJECT_ROOT"`.

### Source: `scripts/local/bootstrap.sh`

```bash
#!/usr/bin/env bash
# Bootstrap a new agentive project from existing design materials.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Resolve TARGET before cd — user may pass a relative path from their cwd
TARGET="${1:?Usage: $0 <target-directory>}"
if [ ! -d "$TARGET" ]; then
    echo "❌ Target directory does not exist: $TARGET"
    exit 1
fi
TARGET="$(cd "$TARGET" && pwd)"
PROJECT_NAME="$(basename "$TARGET")"

# ... rest uses $PROJECT_ROOT as absolute path, no cd needed
```

Key change: Removed `cd "$PROJECT_ROOT"` — bootstrap operates on TWO directories (source PROJECT_ROOT and user-provided TARGET). Previously, the cd happened BEFORE TARGET resolution, breaking relative paths.

### Source: `scripts/core/check-bots.sh` (representative of 4 scripts with `|| exit 1`)

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 1
```

Added `|| exit 1` to `cd` in scripts without `set -e`: check-bots.sh, gh-review-helper.sh, preflight-check.sh, wait-for-bots.sh.

### Source: `scripts/core/ci-check.sh` (representative of scripts with `set -e`)

```bash
set -e  # Exit on first error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"
```

Scripts with `set -e` don't need `|| exit 1` since `set -e` already exits on cd failure.

### Source: `scripts/optional/setup-dev.sh`

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"
```

Fixed depth from `$SCRIPT_DIR/..` (resolved to `scripts/`) to `$SCRIPT_DIR/../..` (correctly resolves to project root).

### Source: `scripts/optional/create-agent.sh`

```bash
if [[ -n "${CREATE_AGENT_PROJECT_ROOT:-}" ]]; then
    PROJECT_ROOT="$CREATE_AGENT_PROJECT_ROOT"
else
    PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fi
cd "$PROJECT_ROOT"
```

Fixed depth and added `cd "$PROJECT_ROOT"`. Preserves existing env var override pattern.

## What the Bots Found

- **BugBot (High)**: bootstrap.sh — `cd "$PROJECT_ROOT"` before TARGET resolution breaks relative paths → Fixed: moved TARGET resolution before cd, removed cd entirely
- **BugBot (Medium)**: verify-ci.sh — `exec "$0"` with relative path breaks after cwd change → Fixed: added `SELF` absolute path variable
- **CodeRabbit (Minor x4)**: Scripts without `set -e` should have `|| exit 1` on cd → Fixed: added to 4 scripts
- **CodeRabbit (Trivial)**: MD022 blank lines in task file → Declined: internal coordination artifact

## Valid Values and Boundaries

- **`SCRIPT_DIR`**: Always absolute (resolved via `cd ... && pwd`). Cannot be empty since `dirname` always returns at least `.`
- **`PROJECT_ROOT`**: Computed as `SCRIPT_DIR/../..`. Could fail if parent directories don't exist (extremely unlikely for installed scripts). Protected by `|| exit 1` or `set -e`.
- **`SELF` (verify-ci.sh)**: Computed from SCRIPT_DIR + basename. Used for `exec` re-invocation in wait mode.
- **`TARGET` (bootstrap.sh)**: User-provided, can be relative or absolute. Must exist as directory before resolution.

## Key Questions

1. In bootstrap.sh, is it safe to not `cd "$PROJECT_ROOT"` at all? The script uses `$PROJECT_ROOT/...` absolute paths for rsync sources, but later does `cd "$TARGET"` for git init. Does any code between lines 42-105 rely on cwd being PROJECT_ROOT?
2. In verify-ci.sh, does `exec "$SELF" "$BRANCH"` correctly pass through the --wait flag? The original `exec "$0"` only passed `$BRANCH`, so the re-exec'd process runs in non-wait mode (intentional — it's re-checking status after the wait completed).
