#!/usr/bin/env bash
# Setup development environment
# Usage: ./scripts/setup-dev.sh
#
# Metadata:
#   version: 1.0.0
#   origin: dispatch-kit
#   origin-version: 0.3.2
#   last-updated: 2026-02-27
#   created-by: "@movito with planner2"
#
# Creates .venv, installs project in editable mode,
# verifies tmux, and runs project init if applicable.
# Safe to re-run (idempotent).

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

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
# Step 1: Find suitable Python (3.10-3.12)
# ─────────────────────────────────────────
echo "1/5 🐍 Finding Python 3.10-3.12..."

PYTHON=""

# Validate a candidate Python: must be executable and report version 3.10-3.12
is_supported_python() {
    local candidate="$1"
    local major minor
    major="$("$candidate" -c 'import sys; print(sys.version_info.major)' 2>/dev/null)" || return 1
    minor="$("$candidate" -c 'import sys; print(sys.version_info.minor)' 2>/dev/null)" || return 1
    [ "$major" -eq 3 ] && [ "$minor" -ge 10 ] && [ "$minor" -lt 13 ]
}

# Search explicit versioned commands first (don't use bare python3 — may be 3.13+)
for candidate in python3.12 python3.11 python3.10; do
    resolved="$(command -v "$candidate" 2>/dev/null)" || continue
    if is_supported_python "$resolved"; then
        PYTHON="$resolved"
        break
    fi
done

# If not found, check Homebrew paths (Apple Silicon + Intel)
if [ -z "$PYTHON" ]; then
    for version in 3.12 3.11 3.10; do
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
    echo "❌ No Python 3.10-3.12 found"
    echo "   Install one of: python3.12, python3.11, python3.10"
    echo "   macOS: brew install python@3.12"
    exit 1
fi

# Report discovered version
PY_VERSION=$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')

echo "✅ Found $PYTHON ($PY_VERSION)"
echo

# ─────────────────────────────────────────
# Step 2: Create .venv (prefer uv)
# ─────────────────────────────────────────
echo "2/5 📦 Setting up virtual environment..."

if [ -d ".venv" ]; then
    # Check existing venv's Python version
    if [ -x ".venv/bin/python" ]; then
        VENV_VERSION=$(".venv/bin/python" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "unknown")
        VENV_MAJOR=$(".venv/bin/python" -c 'import sys; print(sys.version_info.major)' 2>/dev/null || echo "0")
        VENV_MINOR=$(".venv/bin/python" -c 'import sys; print(sys.version_info.minor)' 2>/dev/null || echo "0")

        if [ "$VENV_MAJOR" -eq 3 ] && [ "$VENV_MINOR" -ge 10 ] && [ "$VENV_MINOR" -lt 13 ]; then
            echo "✅ .venv exists with Python $VENV_VERSION (compatible)"
            SUMMARY+=("venv: already exists (Python $VENV_VERSION)")
        else
            echo "❌ .venv exists but has Python $VENV_VERSION (need 3.10-3.12)"
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
echo "3/5 📥 Installing $PROJECT_NAME..."

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
echo "4/5 🖥️  Checking tmux..."

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
# Step 5: Project-specific initialization
# ─────────────────────────────────────────
echo "5/5 ⚙️  Checking project configuration..."

# dispatch-kit: run dispatch init if config is missing
if command -v dispatch >/dev/null 2>&1 || [ -x ".venv/bin/dispatch" ]; then
    if [ -f ".dispatch/config.yml" ]; then
        echo "✅ .dispatch/config.yml exists (skipping init)"
        SUMMARY+=("config: already exists")
    else
        echo "  Running dispatch init..."
        .venv/bin/dispatch init 2>/dev/null || dispatch init 2>/dev/null || true
        if [ -f ".dispatch/config.yml" ]; then
            echo "✅ dispatch init complete"
            SUMMARY+=("config: created via dispatch init")
        else
            echo "⚠️  dispatch init did not create config (dispatch-kit may not be installed)"
            SUMMARY+=("config: skipped (dispatch-kit not available)")
        fi
    fi
else
    echo "✅ No project-specific initialization needed"
    SUMMARY+=("config: N/A")
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
echo "  ./scripts/ci-check.sh        # run CI checks"
