# ASK-0004: Add Scripts Directory with Starter Scripts

**Status**: Done
**Priority**: Medium
**Assigned To**: feature-developer
**Estimated Effort**: 30 minutes
**Created**: 2025-11-28
**Source**: AL2 ADR-0001 (Problem #5)

## Problem Statement

The `scripts/` directory doesn't exist in the starter kit but is referenced in:
- Pre-commit config (`scripts/pre-commit-validate-tasks.sh`)
- Various documentation references

New projects need this directory for:
- Pre-flight verification scripts
- CI helper scripts
- Development utility scripts

## Requirements

### Must Have

- [ ] Create `scripts/` directory
- [ ] Add `scripts/README.md` explaining purpose
- [ ] Add `scripts/verify-setup.sh` for setup verification

### Should Have

- [ ] Add `scripts/verify-ci.sh` for CI status checking
- [ ] Make scripts executable (`chmod +x`)

## Implementation

### 1. Create Directory Structure

```
scripts/
├── README.md
├── verify-setup.sh
└── verify-ci.sh
```

### 2. Create `scripts/README.md`

```markdown
# Scripts Directory

Utility scripts for development and CI/CD operations.

## Available Scripts

### `verify-setup.sh`
Verifies project setup is complete and working:
- Python version check
- Virtual environment
- Dependencies installed
- Pre-commit hooks
- Tests passing

Usage: `./scripts/verify-setup.sh`

### `verify-ci.sh`
Checks GitHub Actions CI status for a branch:
- Lists recent workflow runs
- Shows pass/fail status
- Waits for in-progress runs

Usage: `./scripts/verify-ci.sh [branch-name]`

## Adding New Scripts

1. Create script in this directory
2. Add shebang: `#!/bin/bash`
3. Make executable: `chmod +x scripts/your-script.sh`
4. Add documentation to this README
```

### 3. Create `scripts/verify-setup.sh`

```bash
#!/bin/bash
# Verify project setup is complete and working

set -e

echo "🔍 Verifying project setup..."
echo

ERRORS=0

# Check Python version
echo -n "Python 3.9+: "
if python3 --version 2>/dev/null | grep -qE "Python 3\.(9|1[0-9])"; then
    echo "✅ $(python3 --version)"
else
    echo "❌ Python 3.9+ required"
    ERRORS=$((ERRORS + 1))
fi

# Check virtual environment
echo -n "Virtual environment: "
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ Active ($VIRTUAL_ENV)"
elif [ -d "venv" ] || [ -d ".venv" ]; then
    echo "⚠️  Found but not activated"
else
    echo "❌ Not found (run: python -m venv venv)"
    ERRORS=$((ERRORS + 1))
fi

# Check pytest
echo -n "pytest: "
if command -v pytest &> /dev/null; then
    echo "✅ $(pytest --version | head -1)"
else
    echo "❌ Not installed (run: pip install -e '.[dev]')"
    ERRORS=$((ERRORS + 1))
fi

# Check pre-commit
echo -n "pre-commit: "
if command -v pre-commit &> /dev/null; then
    echo "✅ $(pre-commit --version)"
else
    echo "❌ Not installed (run: pip install pre-commit)"
    ERRORS=$((ERRORS + 1))
fi

# Check pre-commit hooks installed
echo -n "pre-commit hooks: "
if [ -f ".git/hooks/pre-commit" ]; then
    echo "✅ Installed"
else
    echo "⚠️  Not installed (run: pre-commit install)"
fi

# Check tests directory
echo -n "Tests directory: "
if [ -d "tests" ]; then
    TEST_COUNT=$(find tests -name "test_*.py" | wc -l | tr -d ' ')
    echo "✅ Found ($TEST_COUNT test files)"
else
    echo "⚠️  No tests/ directory"
fi

# Summary
echo
if [ $ERRORS -eq 0 ]; then
    echo "✅ Setup verification passed!"
    exit 0
else
    echo "❌ Setup verification failed ($ERRORS errors)"
    exit 1
fi
```

### 4. Create `scripts/verify-ci.sh`

```bash
#!/bin/bash
# Check GitHub Actions CI status for a branch

BRANCH="${1:-$(git branch --show-current)}"

echo "🔍 Checking CI status for branch: $BRANCH"
echo

# Check gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not installed"
    echo "Install: https://cli.github.com/"
    exit 1
fi

# Check gh is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ GitHub CLI not authenticated"
    echo "Run: gh auth login"
    exit 1
fi

# List recent workflow runs
echo "Recent workflow runs:"
gh run list --branch "$BRANCH" --limit 5

echo
echo "To watch a specific run:"
echo "  gh run watch <run-id>"
```

### 5. Make Scripts Executable

```bash
chmod +x scripts/verify-setup.sh
chmod +x scripts/verify-ci.sh
```

## Acceptance Criteria

1. `scripts/` directory exists with README
2. `./scripts/verify-setup.sh` runs and checks project setup
3. `./scripts/verify-ci.sh` checks CI status via gh CLI
4. All scripts are executable

## Testing

```bash
# Test setup verification
./scripts/verify-setup.sh

# Test CI check (requires gh auth)
./scripts/verify-ci.sh main
```

## Related

- ASK-0002 (pre-commit fixes - removes reference to missing script)
- ASK-0003 (gh CLI fix - verify-ci.sh uses gh)
- AL2 ADR-0001 (source of requirements)
