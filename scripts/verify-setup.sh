#!/bin/bash
# Verify project setup is complete and working
# Usage: ./scripts/verify-setup.sh

set -e

echo "🔍 Verifying project setup..."
echo

ERRORS=0
WARNINGS=0

# Check Python version (>=3.10, <3.13 required for adversarial-workflow)
echo -n "Python 3.10-3.12: "
PY_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "0.0.0")
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 10 ] && [ "$PY_MINOR" -lt 13 ]; then
    echo "✅ Python $PY_VERSION"
elif [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    echo "❌ Python $PY_VERSION is too old (3.10+ required)"
    ERRORS=$((ERRORS + 1))
else
    echo "❌ Python $PY_VERSION is too new (<3.13 required)"
    echo "   adversarial-workflow requires Python >=3.10,<3.13"
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
