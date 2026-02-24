# ASK-0001: Add Generic pyproject.toml

**Status**: Done
**Priority**: Critical
**Assigned To**: feature-developer
**Estimated Effort**: 30 minutes
**Created**: 2025-11-28
**Source**: AL2 ADR-0001 (Problems #1, #2)

## Problem Statement

New projects cloned from the starter kit have no `pyproject.toml`, requiring 15+ minutes to configure from scratch. Additionally, without explicit package configuration, setuptools discovers `agents/` and `delegation/` as Python packages, causing pip install failures.

## Requirements

### Must Have

- [ ] Create `pyproject.toml` with placeholder project name
- [ ] Include dev dependencies (pytest, black, ruff, pre-commit)
- [ ] Add `[tool.setuptools] packages = []` to prevent auto-discovery errors
- [ ] Configure pytest (testpaths, markers)
- [ ] Configure black (line-length=88)
- [ ] Configure ruff (line-length=88, select rules)

### Should Have

- [ ] Include isort config compatible with black
- [ ] Add coverage configuration
- [ ] Document placeholders with comments

## Implementation

Create `/pyproject.toml`:

```toml
[project]
name = "your-project-name"  # TODO: Change this to your project name
version = "0.1.0"
description = "Your project description"
readme = "README.md"
requires-python = ">=3.9"
dependencies = []  # Add runtime dependencies as needed

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.12.0",
    "ruff>=0.1.0",
    "isort>=5.13.0",
    "pre-commit>=3.5.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
# Prevent auto-discovery of non-Python directories (agents/, delegation/)
# Add your packages here when you create them, e.g.: packages = ["your_project"]
packages = []

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
]
addopts = "-v --tb=short"

[tool.black]
line-length = 88
target-version = ["py39", "py310", "py311"]

[tool.ruff]
line-length = 88
select = ["E", "F", "W", "I"]
ignore = ["E203", "W503"]

[tool.isort]
profile = "black"
line_length = 88
```

## Acceptance Criteria

1. `pip install -e ".[dev]"` works on fresh clone
2. No setuptools auto-discovery errors
3. `pytest` finds and runs tests in `tests/` directory
4. All tool configurations are present and functional

## Testing

```bash
# Fresh clone simulation
git clone <repo> test-project
cd test-project
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"  # Should succeed
pytest --collect-only    # Should find tests
```

## Related

- AL2 ADR-0001 (source of requirements)
- ASK-0002 (pre-commit fixes, depends on this)
