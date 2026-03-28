#!/bin/bash
# Verify project setup is complete and working
# Usage: ./scripts/verify-setup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "🔍 Verifying project setup..."
echo

ERRORS=0
WARNINGS=0

# Read Python version constraint from pyproject.toml, fallback to >=3.10
PY_MIN=10
PY_MAX=13
PROJECT_NAME="this project"
if [ -f "pyproject.toml" ]; then
    _PY_REQUIRES=$(python3 -c "
import pathlib, re
try:
    import tomllib
except ImportError:
    import tomli as tomllib
p = pathlib.Path('pyproject.toml')
data = tomllib.loads(p.read_text(encoding='utf-8'))
req = data.get('project', {}).get('requires-python', '')
print(req)
" 2>/dev/null || true)
    if [ -n "$_PY_REQUIRES" ]; then
        _MIN=$(echo "$_PY_REQUIRES" | grep -oE '>=3\.([0-9]+)' | grep -oE '[0-9]+$')
        _MAX=$(echo "$_PY_REQUIRES" | grep -oE '<3\.([0-9]+)' | grep -oE '[0-9]+$')
        [ -n "$_MIN" ] && PY_MIN="$_MIN"
        [ -n "$_MAX" ] && PY_MAX="$_MAX"
    fi
    PROJECT_NAME=$(python3 -c "
import pathlib
try:
    import tomllib
except ImportError:
    import tomli as tomllib
p = pathlib.Path('pyproject.toml')
print(tomllib.loads(p.read_text(encoding='utf-8')).get('project', {}).get('name', 'this project'))
" 2>/dev/null || echo "this project")
fi

# Check Python version
echo -n "Python 3.${PY_MIN}-3.$((PY_MAX - 1)): "
PY_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "0.0.0")
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge "$PY_MIN" ] && [ "$PY_MINOR" -lt "$PY_MAX" ]; then
    echo "✅ Python $PY_VERSION"
elif [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt "$PY_MIN" ]; }; then
    echo "❌ Python $PY_VERSION is too old (3.${PY_MIN}+ required)"
    ERRORS=$((ERRORS + 1))
else
    echo "❌ Python $PY_VERSION is too new (<3.${PY_MAX} required)"
    echo "   $PROJECT_NAME requires Python >=3.${PY_MIN},<3.${PY_MAX}"
    ERRORS=$((ERRORS + 1))
fi

# Check virtual environment
echo -n "Virtual environment: "
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ Active ($(basename "$VIRTUAL_ENV"))"
elif [ -d "venv" ]; then
    echo "⚠️  Found ./venv but not activated"
    echo "   Run: source venv/bin/activate"
    WARNINGS=$((WARNINGS + 1))
elif [ -d ".venv" ]; then
    echo "⚠️  Found ./.venv but not activated"
    echo "   Run: source .venv/bin/activate"
    WARNINGS=$((WARNINGS + 1))
else
    echo "❌ Not found"
    echo "   Run: python -m venv venv && source venv/bin/activate"
    ERRORS=$((ERRORS + 1))
fi

# Check pytest
echo -n "pytest: "
if command -v pytest &> /dev/null; then
    echo "✅ $(pytest --version 2>&1 | head -1)"
else
    echo "❌ Not installed"
    echo "   Run: pip install -e '.[dev]'"
    ERRORS=$((ERRORS + 1))
fi

# Check pre-commit
echo -n "pre-commit: "
if command -v pre-commit &> /dev/null; then
    echo "✅ $(pre-commit --version 2>&1)"
else
    echo "❌ Not installed"
    echo "   Run: pip install pre-commit"
    ERRORS=$((ERRORS + 1))
fi

# Check pre-commit hooks installed
echo -n "pre-commit hooks: "
if [ -f ".git/hooks/pre-commit" ]; then
    echo "✅ Installed"
else
    echo "⚠️  Not installed"
    echo "   Run: pre-commit install"
    WARNINGS=$((WARNINGS + 1))
fi

# Check tests directory
echo -n "Tests directory: "
if [ -d "tests" ]; then
    TEST_COUNT=$(find tests -name "test_*.py" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$TEST_COUNT" -gt 0 ]; then
        echo "✅ Found ($TEST_COUNT test files)"
    else
        echo "⚠️  Directory exists but no test_*.py files"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "⚠️  No tests/ directory"
    WARNINGS=$((WARNINGS + 1))
fi

# Check pyproject.toml
echo -n "pyproject.toml: "
if [ -f "pyproject.toml" ]; then
    echo "✅ Found"
else
    echo "❌ Not found"
    ERRORS=$((ERRORS + 1))
fi

# Check gh CLI (optional)
echo -n "GitHub CLI (gh): "
if command -v gh &> /dev/null; then
    if gh auth status &> /dev/null; then
        echo "✅ Installed and authenticated"
    else
        echo "⚠️  Installed but not authenticated"
        echo "   Run: gh auth login"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "⚠️  Not installed (optional, needed for CI checks)"
    WARNINGS=$((WARNINGS + 1))
fi

# Summary
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ Setup verification passed!"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  Setup mostly complete ($WARNINGS warnings)"
    exit 0
else
    echo "❌ Setup verification failed ($ERRORS errors, $WARNINGS warnings)"
    exit 1
fi
