# ASK-0002: Fix Pre-commit Configuration

**Status**: Done
**Priority**: Critical
**Assigned To**: feature-developer
**Estimated Effort**: 45 minutes
**Created**: 2025-11-28
**Source**: AL2 ADR-0001 (Problems #3, #4, #6, #7)
**Depends On**: ASK-0001 (pyproject.toml)

## Problem Statement

The `.pre-commit-config.yaml` has several issues that cause failures on new projects:

1. **Hardcoded paths**: `./venv/bin/pytest` assumes specific venv location
2. **Missing script**: `scripts/pre-commit-validate-tasks.sh` doesn't exist
3. **Project-specific naming**: Header says "Thematic Cuts"
4. **Trailing whitespace**: Many starter kit files have trailing whitespace

## Requirements

### Must Have

- [ ] Remove hardcoded `./venv/bin/` paths - use PATH resolution
- [ ] Remove or stub the `validate-tasks` hook
- [ ] Update header comment to generic project name
- [ ] Run `pre-commit run --all-files` to fix whitespace issues

### Should Have

- [ ] Add comments explaining each hook section
- [ ] Document how to skip tests (`SKIP_TESTS=1`)
- [ ] Make pytest hook more robust (check if tests exist first)

## Implementation

### 1. Update `.pre-commit-config.yaml`

**Header change:**
```yaml
# Pre-commit hooks configuration
# See https://pre-commit.com for more information
#
# Setup: pre-commit install
# Skip tests: SKIP_TESTS=1 git commit -m "WIP"
```

**Remove validate-tasks hook** (lines 57-65) - project-specific, script doesn't exist.

**Fix pytest hook** (lines 71-80):
```yaml
  - repo: local
    hooks:
      - id: pytest-fast
        name: Run fast tests (pre-commit guard)
        entry: bash -c 'if [ "$SKIP_TESTS" = "1" ]; then echo "Skipping tests (SKIP_TESTS=1)"; exit 0; fi; if [ -d "tests" ] && [ -n "$(ls -A tests/*.py 2>/dev/null)" ]; then pytest tests/ -v --tb=short -x -m "not slow" --maxfail=3 || (echo ""; echo "Fast tests failed! Fix before committing or use:"; echo "  SKIP_TESTS=1 git commit -m \"WIP\""; exit 1); else echo "No tests found, skipping"; fi'
        language: system
        pass_filenames: false
        always_run: true
        stages: [pre-commit]
        verbose: true
```

Key changes:
- Removed `./venv/bin/` prefix (use PATH)
- Added check for tests directory existence
- Removed emoji (terminal compatibility)

### 2. Fix Trailing Whitespace

```bash
# Install pre-commit if needed
pip install pre-commit

# Run all hooks to fix whitespace
pre-commit run trailing-whitespace --all-files
pre-commit run end-of-file-fixer --all-files

# Commit the fixes
git add -A
git commit -m "fix: Remove trailing whitespace from starter kit files"
```

## Acceptance Criteria

1. Pre-commit hooks pass on fresh clone after `pip install -e ".[dev]" && pre-commit install`
2. No hardcoded venv paths in config
3. No references to "Thematic Cuts" or project-specific scripts
4. All starter kit files pass whitespace checks

## Testing

```bash
# Fresh clone test
git clone <repo> test-project
cd test-project
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
pre-commit install
pre-commit run --all-files  # Should pass
```

## Related

- ASK-0001 (pyproject.toml - must be done first)
- ASK-0004 (scripts directory)
- AL2 ADR-0001 (source of requirements)
