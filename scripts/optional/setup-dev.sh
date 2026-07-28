#!/usr/bin/env bash
# Setup development environment
# Usage: ./scripts/optional/setup-dev.sh [--with-dispatch]
#
# Metadata:
#   version: 1.1.0
#   origin: dispatch-kit
#   origin-version: 0.3.2
#   last-updated: 2026-07-28
#   created-by: "@movito with planner2"
#
# Creates .venv, installs the project in editable mode, and verifies
# tmux. Safe to re-run (idempotent).
#
# --with-dispatch (KIT-0067 D4/A18): additionally install dispatch-kit
# from a local clone and run `dispatch init`. dispatch-kit is NOT on
# PyPI — this only works on a machine that has the clone (default
# ~/Github/dispatch-kit; override with DISPATCH_KIT_PATH). The default
# run skips both steps so this script works on any machine.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

WITH_DISPATCH=0
for arg in "$@"; do
    case "$arg" in
        --with-dispatch)
            WITH_DISPATCH=1
            ;;
        -h|--help)
            echo "Usage: ./scripts/optional/setup-dev.sh [--with-dispatch]"
            echo
            echo "  --with-dispatch  also install dispatch-kit from a local clone"
            echo "                   (not on PyPI; DISPATCH_KIT_PATH overrides the"
            echo "                   default ~/Github/dispatch-kit) and run"
            echo "                   'dispatch init'"
            exit 0
            ;;
        *)
            echo "Error: unknown argument: $arg"
            echo "Usage: ./scripts/optional/setup-dev.sh [--with-dispatch]"
            exit 1
            ;;
    esac
done

# Step numbering adapts to the dispatch opt-in (4 base steps, 6 with)
if [ "$WITH_DISPATCH" -eq 1 ]; then
    TOTAL_STEPS=6
else
    TOTAL_STEPS=4
fi
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
# Step 3 (opt-in): Install dispatch-kit (local)
# ─────────────────────────────────────────
# Gated behind --with-dispatch (KIT-0067 D4/A18): installs from a
# hardcoded operator-machine clone and is skipped by default so the
# door's venv offer works on any machine.
if [ "$WITH_DISPATCH" -eq 1 ]; then
step_banner "🚀 Installing dispatch-kit..."

# dispatch-kit is not yet on PyPI — install from local clone.
# Override the path with DISPATCH_KIT_PATH env var if needed.
DISPATCH_KIT_PATH="${DISPATCH_KIT_PATH:-$HOME/Github/dispatch-kit}"

if .venv/bin/python -c "import dispatch_kit" 2>/dev/null; then
    DK_VER=$(.venv/bin/python -c "from importlib.metadata import version; print(version('dispatch-kit'))" 2>/dev/null || echo "unknown")
    echo "✅ dispatch-kit $DK_VER already installed"
    SUMMARY+=("dispatch-kit: already installed ($DK_VER)")
elif [ -d "$DISPATCH_KIT_PATH" ] && [ -f "$DISPATCH_KIT_PATH/pyproject.toml" ]; then
    echo "  Installing from $DISPATCH_KIT_PATH..."
    if command -v uv >/dev/null 2>&1; then
        uv pip install -e "$DISPATCH_KIT_PATH" --python .venv/bin/python
    else
        .venv/bin/pip install -e "$DISPATCH_KIT_PATH"
    fi
    DK_VER=$(.venv/bin/python -c "from importlib.metadata import version; print(version('dispatch-kit'))" 2>/dev/null || echo "unknown")
    echo "✅ dispatch-kit $DK_VER installed from local repo"
    SUMMARY+=("dispatch-kit: installed from local ($DK_VER)")
else
    # --with-dispatch is an explicit request — an unmet one is a
    # failure, never a warning-that-reads-as-success (CodeRabbit,
    # PR #98). The skip-quietly behavior is the DEFAULT mode's.
    echo "❌ dispatch-kit requested (--with-dispatch) but no clone found"
    echo "   Set DISPATCH_KIT_PATH or clone to ~/Github/dispatch-kit/"
    exit 1
fi
echo
fi  # WITH_DISPATCH (step 3)

# ─────────────────────────────────────────
# Step: Install project (editable)
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
# Step 5: Check tmux availability
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
# Step (opt-in): dispatch-kit initialization
# ─────────────────────────────────────────
if [ "$WITH_DISPATCH" -eq 1 ]; then
step_banner "⚙️  Checking dispatch configuration..."

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
            # explicit opt-in unmet -> failure (CodeRabbit, PR #98)
            echo "❌ dispatch init did not create .dispatch/config.yml"
            exit 1
        fi
    fi
else
    # explicit opt-in unmet -> failure (CodeRabbit, PR #98)
    echo "❌ --with-dispatch requested but no dispatch CLI found after install"
    exit 1
fi
echo
else
    echo "ℹ️  dispatch-kit steps skipped (not on PyPI; opt in with --with-dispatch)"
    SUMMARY+=("dispatch-kit: skipped (opt in with --with-dispatch)")
    echo
fi  # WITH_DISPATCH (init step)

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
