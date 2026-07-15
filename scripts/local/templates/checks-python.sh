#!/bin/bash
# checks.sh — this project's check hook (seeded by bootstrap; consumer-owned).
#
# Contract (KIT-ADR-0027 P1): accepts `--mode ci|local`; exits 0 (pass)
# or 1 (fail) only; human-readable diagnostics to stdout; invoked from
# the repo root with no other environment guarantees. Nothing else is
# passed through. ci-check.sh dispatches here when this file exists.
# Edit freely — the kit never overwrites this file after seeding.
#
# Profile: python — the kit's own gauntlet (Black, isort, flake8,
# pattern lint, pytest + coverage, cross-repo config), moved here from
# ci-check.sh's built-in checks. Both modes currently run the same set;
# differentiate them (e.g. skip coverage in --mode local) as your
# project needs.

MODE=""
case "${1:-}" in
    --mode) MODE="${2:-}" ;;
    --mode=*) MODE="${1#--mode=}" ;;
esac
if [ "$MODE" != "ci" ] && [ "$MODE" != "local" ]; then
    echo "Usage: $0 --mode ci|local"
    echo "   Unknown or missing mode: '${MODE:-<none>}'"
    exit 1
fi

set -e  # Exit on first error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CORE_DIR="$PROJECT_ROOT/scripts/core"
cd "$PROJECT_ROOT"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Running local CI checks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Track overall status
FAILED=0

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    # Try to activate local venv
    if [ -f ".venv/bin/activate" ]; then
        echo "📦 Activating virtual environment..."
        source .venv/bin/activate
    elif [ -f "venv/bin/activate" ]; then
        echo "📦 Activating virtual environment..."
        source venv/bin/activate
    else
        echo "⚠️  No virtual environment found. Using system Python."
    fi
fi

echo "Python: $(which python3)"
echo

# Preflight: verify flake8 is installed before running lint steps.
# Fail fast with a clear message rather than emitting an opaque
# "command not found" when the dev extras haven't been installed.
if ! python3 -m flake8 --version >/dev/null 2>&1; then
    echo "❌ ERROR: flake8 not installed — run 'python3 -m pip install -e \".[dev]\"'" >&2
    exit 1
fi

# Preflight: warn (never fail) when the active Black differs from the
# pyproject.toml pin. A stale venv reads as a phantom formatting failure
# on changes that can't affect Black (KIT-0032 retro: venv 23.12.1 vs
# pinned 26.x failed a markdown-only change). The Black step below stays
# the gate — this only names the real cause up front. isort is pinned as
# a floor (>=), not an exact version, so no drift check applies there.
PINNED_BLACK=$(grep -Eo 'black==[0-9][0-9A-Za-z.]*' pyproject.toml 2>/dev/null | head -1 | sed 's/^black==//')
ACTIVE_BLACK=$(black --version 2>/dev/null | head -1 | grep -Eo '[0-9]+\.[0-9][0-9A-Za-z.]*' | head -1)
if [ -n "$PINNED_BLACK" ] && [ -n "$ACTIVE_BLACK" ] && [ "$PINNED_BLACK" != "$ACTIVE_BLACK" ]; then
    echo "⚠️  Active Black $ACTIVE_BLACK differs from pyproject.toml pin $PINNED_BLACK"
    echo "   A stale venv can fail formatting that pinned/CI Black accepts."
    echo "   Fix: python3 -m pip install -e \".[dev]\""
    echo
fi

# 1. Black formatting check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1/6 🎨 Checking formatting with Black..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if black --check --diff . 2>/dev/null; then
    echo "✅ Black: All files formatted correctly"
else
    echo "❌ Black: Formatting issues found"
    echo "   Run: black . to fix"
    FAILED=1
fi
echo

# 2. isort import sorting check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2/6 📋 Checking import sorting with isort..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if isort --check-only --diff . 2>/dev/null; then
    echo "✅ isort: Imports sorted correctly"
else
    echo "❌ isort: Import sorting issues found"
    echo "   Run: isort . to fix"
    FAILED=1
fi
echo

# 3. flake8 linting
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3/6 🔎 Linting with flake8..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if python3 -m flake8 scripts/ tests/ --max-line-length=88 --extend-ignore=E203,W503 --select=E9,F63,F7,F82 2>/dev/null; then
    echo "✅ flake8: No critical linting errors"
else
    echo "❌ flake8: Linting errors found"
    FAILED=1
fi
echo

# 4. Pattern lint (project-specific DK rules)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4/6 🔍 Running pattern lint (DK rules)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PY_FILES=$(find scripts/ tests/ -name '*.py' 2>/dev/null)
if [ -n "$PY_FILES" ]; then
    if python3 "$CORE_DIR/pattern_lint.py" $PY_FILES 2>&1; then
        echo "✅ Pattern lint: No DK violations"
    else
        echo "❌ Pattern lint: DK violations found"
        echo "   Fix violations or add # noqa: DKxxx to suppress"
        FAILED=1
    fi
else
    echo "⚠️  No Python files found in scripts/ or tests/"
fi
echo

# 5. Full test suite with coverage
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5/6 🧪 Running full test suite with coverage..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if pytest tests/ -v --cov=scripts --cov-report=term-missing; then
    echo "✅ Tests: All tests pass (fail_under gate in pyproject.toml)"
else
    echo "❌ Tests: Test failures or coverage below pyproject gate"
    FAILED=1
fi
echo

# 6. Cross-repo config validation (KIT-0030 / KIT-ADR-0024 §2)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6/6 🧭 Validating cross-repo config..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
# Exits 1 on FAIL (declared cross-repo but no parseable ## Target Repository
# section); 0 on PASS or WARN (warning printed for a missing local target).
if python3 "$CORE_DIR/check_cross_repo_config.py" "$PROJECT_ROOT"; then
    :
else
    echo "   Fix CLAUDE.md's ## Target Repository section."
    FAILED=1
fi
echo

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $FAILED -eq 0 ]; then
    echo "✅ All CI checks passed!"
    echo "   Safe to push: git push origin $(git branch --show-current)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 0
else
    echo "❌ CI checks failed!"
    echo "   Fix the issues above before pushing."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 1
fi
