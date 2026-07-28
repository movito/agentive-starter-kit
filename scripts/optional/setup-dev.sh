#!/usr/bin/env bash
# Setup development environment
# Usage: ./scripts/optional/setup-dev.sh
#
# Metadata:
#   version: 2.0.0
#   origin: dispatch-kit
#   origin-version: 0.3.2
#   last-updated: 2026-07-28
#   created-by: "@movito with planner2"
#
# Creates .venv, installs the project in editable mode, and verifies
# tmux. Safe to re-run (idempotent).
#
# The --with-dispatch opt-in (KIT-0067 D4/A18) was removed in KIT-0077
# when dispatch-kit was retired; the script now takes no arguments.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

for arg in "$@"; do
    case "$arg" in
        -h|--help)
            echo "Usage: ./scripts/optional/setup-dev.sh"
            echo
            echo "Creates .venv, installs the project in editable mode,"
            echo "and checks for tmux. Takes no options."
            exit 0
            ;;
        *)
            echo "Error: unknown argument: $arg"
            echo "Usage: ./scripts/optional/setup-dev.sh"
            exit 1
            ;;
    esac
done

TOTAL_STEPS=4
STEP=0
step_banner() {
    STEP=$((STEP + 1))
    echo "$STEP/$TOTAL_STEPS $1"
}

# Detect project name from pyproject.toml or directory name
PROJECT_NAME=""
if [ -f "pyproject.toml" ]; then
    PROJECT_NAME=$(grep -m1 '^name\s*=' pyproject.toml | sed 's/.*=\s*"\(.*\)"/\1/' 2>/dev/null || true)
fi
if [ -z "$PROJECT_NAME" ]; then
    PROJECT_NAME=$(basename "$PROJECT_ROOT")
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 Setting up $PROJECT_NAME development environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Track what we did for the summary
SUMMARY=()

# ─────────────────────────────────────────
# Step 1: Find suitable Python (3.10+)
# ─────────────────────────────────────────
step_banner "🐍 Finding Python 3.10+..."

PYTHON=""

# Validate a candidate Python: must be executable and report version 3.10+
is_supported_python() {
    local candidate="$1"
    local major minor
    major="$("$candidate" -c 'import sys; print(sys.version_info.major)' 2>/dev/null)" || return 1
    minor="$("$candidate" -c 'import sys; print(sys.version_info.minor)' 2>/dev/null)" || return 1
    [ "$major" -eq 3 ] && [ "$minor" -ge 10 ]
}

# Prefer explicit versioned commands (newest first), then bare python3
for candidate in python3.14 python3.13 python3.12 python3.11 python3.10 python3; do
    resolved="$(command -v "$candidate" 2>/dev/null)" || continue
    if is_supported_python "$resolved"; then
        PYTHON="$resolved"
        break
    fi
done

# If not found, check Homebrew paths (Apple Silicon + Intel)
if [ -z "$PYTHON" ]; then
    for version in 3.14 3.13 3.12 3.11 3.10; do
        for prefix in /opt/homebrew/opt /usr/local/opt; do
            candidate="$prefix/python@$version/bin/python$version"
            if [ -x "$candidate" ] && is_supported_python "$candidate"; then
                PYTHON="$candidate"
                break 2
            fi
        done
    done
fi

if [ -z "$PYTHON" ]; then
    echo "❌ No Python 3.10+ found"
    echo "   Install a recent Python 3 (3.10 or newer)"
    echo "   macOS: brew install python@3.14"
    exit 1
fi

# Report discovered version
PY_VERSION=$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')

echo "✅ Found $PYTHON ($PY_VERSION)"
echo

# ─────────────────────────────────────────
# Step 2: Create .venv (prefer uv)
# ─────────────────────────────────────────
step_banner "📦 Setting up virtual environment..."

if [ -d ".venv" ]; then
    # Check existing venv's Python version
    if [ -x ".venv/bin/python" ]; then
        VENV_VERSION=$(".venv/bin/python" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "unknown")
        VENV_MAJOR=$(".venv/bin/python" -c 'import sys; print(sys.version_info.major)' 2>/dev/null || echo "0")
        VENV_MINOR=$(".venv/bin/python" -c 'import sys; print(sys.version_info.minor)' 2>/dev/null || echo "0")

        if [ "$VENV_MAJOR" -eq 3 ] && [ "$VENV_MINOR" -ge 10 ]; then
            echo "✅ .venv exists with Python $VENV_VERSION (compatible)"
            SUMMARY+=("venv: already exists (Python $VENV_VERSION)")
        else
            echo "❌ .venv exists but has Python $VENV_VERSION (need 3.10+)"
            echo "   Remove .venv manually and re-run: rm -rf .venv"
            exit 1
        fi
    else
        echo "❌ .venv exists but has no working Python"
        echo "   Remove .venv manually and re-run: rm -rf .venv"
        exit 1
    fi
else
    # Create new venv
    if command -v uv >/dev/null 2>&1; then
        echo "  Using uv to create venv..."
        uv venv .venv --python "$PYTHON"
        SUMMARY+=("venv: created with uv (Python $PY_VERSION)")
    else
        echo "  Using python -m venv..."
        "$PYTHON" -m venv .venv
        SUMMARY+=("venv: created with python -m venv (Python $PY_VERSION)")
    fi
    echo "✅ Created .venv"
fi
echo

# ─────────────────────────────────────────
# Step 3: Install project (editable)
# ─────────────────────────────────────────
step_banner "📥 Installing $PROJECT_NAME..."

# Use full paths — don't rely on source activate
if command -v uv >/dev/null 2>&1; then
    echo "  Using uv pip install..."
    uv pip install -e ".[dev]" --python .venv/bin/python
    SUMMARY+=("install: uv pip install -e '.[dev]'")
else
    echo "  Using pip install..."
    .venv/bin/pip install --upgrade pip >/dev/null 2>&1 || true
    .venv/bin/pip install -e ".[dev]"
    SUMMARY+=("install: pip install -e '.[dev]'")
fi
echo "✅ $PROJECT_NAME installed in editable mode"
echo

# ─────────────────────────────────────────
# Step 4: Check tmux availability
# ─────────────────────────────────────────
step_banner "🖥️  Checking tmux..."

if command -v tmux >/dev/null 2>&1; then
    TMUX_VERSION=$(tmux -V 2>/dev/null || echo "unknown")
    echo "✅ tmux available ($TMUX_VERSION)"
    SUMMARY+=("tmux: available ($TMUX_VERSION)")
else
    echo "⚠️  tmux not found (optional — needed for agent spawning)"
    echo "   Install tmux with your package manager (macOS: brew install tmux)"
    SUMMARY+=("tmux: NOT FOUND (optional)")
fi
echo

# ─────────────────────────────────────────
# Summary
# ─────────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Development environment ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
for item in "${SUMMARY[@]}"; do
    echo "  • $item"
done
echo
echo "Next steps:"
echo "  source .venv/bin/activate    # activate the venv"
echo "  ./scripts/core/ci-check.sh        # run CI checks"
