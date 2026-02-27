#!/bin/bash
# Local CI check - mirrors GitHub Actions test.yml
# Run this BEFORE pushing to catch issues early
#
# Usage: ./scripts/ci-check.sh
#
# This script runs the SAME checks as GitHub Actions:
#   1. Black formatting check
#   2. isort import sorting check
#   3. flake8 linting
#   4. Pattern lint (project-specific DK rules)
#   5. Full test suite with coverage (80% threshold)
#
# Run this before every push to prevent CI failures.

set -e  # Exit on first error

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

echo "Python: $(which python)"
echo

# 1. Black formatting check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1/5 🎨 Checking formatting with Black..."
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
echo "2/5 📋 Checking import sorting with isort..."
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
echo "3/5 🔎 Linting with flake8..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if flake8 scripts/ tests/ --max-line-length=88 --extend-ignore=E203,W503 --select=E9,F63,F7,F82 2>/dev/null; then
    echo "✅ flake8: No critical linting errors"
else
    echo "❌ flake8: Linting errors found"
    FAILED=1
fi
echo

# 4. Pattern lint (project-specific DK rules)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4/5 🔍 Running pattern lint (DK rules)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PY_FILES=$(find scripts/ tests/ -name '*.py' 2>/dev/null)
if [ -n "$PY_FILES" ]; then
    if python3 scripts/pattern_lint.py $PY_FILES 2>&1; then
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
echo "5/5 🧪 Running full test suite with coverage..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if pytest tests/ -v --cov=scripts --cov-report=term-missing --cov-fail-under=80; then
    echo "✅ Tests: All tests pass with coverage ≥80%"
else
    echo "❌ Tests: Test failures or coverage below 80%"
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
